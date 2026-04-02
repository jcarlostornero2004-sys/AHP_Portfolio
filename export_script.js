const fs = require('fs');
const path = require('path');

const rootDirs = [
    "c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio\\apps\\api",
    "c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio\\apps\\web\\src",
    "c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio\\apps\\web\\package.json",
    "c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio\\apps\\web\\next.config.ts"
];

const outputFile = "c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio\\codigo_completo.txt";

const ignoreDirs = [".git", "__pycache__", "node_modules", ".next", "public"];
const ignoreExtensions = [".pyc", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".xlsx", ".zip", ".json"];

let outputContent = "# Código de la Aplicación (AHP Portfolio)\n\nA continuación se presenta el código completo de la aplicación (Frontend en Next.js y Backend en Python FastAPI).\n";

function processPath(currentPath) {
    if (!fs.existsSync(currentPath)) return;
    
    const stats = fs.statSync(currentPath);
    if (stats.isFile()) {
        const ext = path.extname(currentPath).toLowerCase();
        // Allow package.json specifically
        if (ignoreExtensions.includes(ext) && !currentPath.endsWith('package.json')) {
            return;
        }
        try {
            const content = fs.readFileSync(currentPath, 'utf8');
            const relativePath = path.relative("c:\\Users\\jcarl\\OneDrive\\Mierda\\ahp_portfolio", currentPath);
            outputContent += `\n\n${'='.repeat(80)}\n`;
            outputContent += `File: ${relativePath}\n`;
            outputContent += `${'='.repeat(80)}\n\n`;
            
            let lang = ext.substring(1);
            if (lang === 'ts' || lang === 'tsx') lang = 'typescript';
            if (lang === 'js' || lang === 'jsx') lang = 'javascript';
            if (lang === 'py') lang = 'python';
            
            outputContent += `\`\`\`${lang}\n${content}${content.endsWith('\n') ? '' : '\n'}\`\`\`\n`;
        } catch(e) {}
    } else if (stats.isDirectory()) {
        const dirname = path.basename(currentPath);
        if (ignoreDirs.includes(dirname)) return;
        
        const files = fs.readdirSync(currentPath);
        for (const file of files) {
            processPath(path.join(currentPath, file));
        }
    }
}

rootDirs.forEach(processPath);
fs.writeFileSync(outputFile, outputContent, 'utf8');
console.log('Exportación completada. Archivo guardado en: ' + outputFile);
