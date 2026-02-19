const fs = require('fs-extra');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const XlsxPopulate = require('xlsx-populate'); 
const csv = require('csv-parser');
const prompt = require('prompt-sync')();

// Configuration
const GOTENBERG_URL = 'http://localhost:3000/forms/libreoffice/convert';

/**
 * 1. Read and Parse CSV Data
 */
function readCsvData(filePath) {
    return new Promise((resolve, reject) => {
        const results = [];
        fs.createReadStream(filePath)
            .pipe(csv())
            .on('data', (data) => {
                const rowArray = [];
                for (const key in data) {
                    let val = data[key];
                    if (!isNaN(val) && val.trim() !== '') {
                        rowArray.push(parseFloat(val));
                    } else {
                        rowArray.push(val);
                    }
                }
                results.push(rowArray);
            })
            .on('end', () => resolve(results))
            .on('error', (error) => reject(error));
    });
}

/**
 * 2. Feed Data into Excel Template (Preserving Charts)
 */
async function generateExcel(templatePath, rawData) {
    // Load workbook using xlsx-populate to keep charts intact
    const workbook = await XlsxPopulate.fromFileAsync(templatePath);

    // --- 1. FEED DATA INTO 'DashboardData' ---
    let dataSheet = workbook.sheet('DashboardData');
    if (!dataSheet) {
        dataSheet = workbook.addSheet('DashboardData');
    }

    // xlsx-populate superpower: dumps a massive 2D array instantly.
    // We start at cell A2 to avoid overwriting your row 1 headers.
    dataSheet.cell("A2").value(rawData);

    // Hide the data sheet so only the Dashboard prints
    dataSheet.hidden(true);

    const tempFilePath = path.join(__dirname, 'temp_ready_to_print.xlsx');
    await workbook.toFileAsync(tempFilePath);
    return tempFilePath;
}

/**
 * 3. Convert to PDF using Gotenberg
 */
async function convertToPdf(excelPath, outputPath) {
    const form = new FormData();
    form.append('files', fs.createReadStream(excelPath));
    
    // Print Page 1 only
    form.append('pageRanges', '1');

    try {
        const response = await axios.post(GOTENBERG_URL, form, {
            headers: { ...form.getHeaders() },
            responseType: 'arraybuffer' 
        });

        fs.writeFileSync(outputPath, response.data);
        return true;
    } catch (error) {
        console.error("Gotenberg Error:", error.message);
        return false;
    }
}

/**
 * Main Execution Function
 */
async function main() {
    console.log("--- 🏭 Data Feeder & PDF Generator ---");

    const csvPath = prompt('Enter path to Raw CSV Data: ').replace(/"/g, '');
    const templatePath = prompt('Enter path to Excel Template: ').replace(/"/g, '');
    
    if (!fs.existsSync(csvPath) || !fs.existsSync(templatePath)) {
        console.error("❌ Error: One of the files does not exist!");
        return;
    }

    const outputDir = path.dirname(templatePath);
    const pdfName = `Factory_Dashboard_${Date.now()}.pdf`;
    const outputPath = path.join(outputDir, pdfName);

    try {
        console.log("⏳ 1/3 Reading CSV Data...");
        const data = await readCsvData(csvPath);

        console.log("⏳ 2/3 Injecting Data (Preserving Charts)...");
        const tempExcel = await generateExcel(templatePath, data);

        console.log("⏳ 3/3 Sending to Gotenberg...");
        const success = await convertToPdf(tempExcel, outputPath);

        if (fs.existsSync(tempExcel)) fs.unlinkSync(tempExcel);

        if (success) {
            console.log(`\n✅ Success! Clean PDF with CHARTS generated at: \n${outputPath}`);
        } else {
            console.log("\n❌ Failed to generate PDF.");
        }

    } catch (err) {
        console.error("Fatal Error:", err);
    }
}

main();