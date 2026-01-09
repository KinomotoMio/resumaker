/**
 * Resume PDF Generator
 *
 * 将简历导出为矢量 PDF（文字可选中，高清晰度）
 *
 * 使用方法:
 *   node generate-resume-pdf.js          # 缩放适应 A4
 *   node generate-resume-pdf.js --natural # 保持原始尺寸，不缩放
 *   node generate-resume-pdf.js --input path/to/file.html --output path/to/output.pdf
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

/**
 * 获取 Chrome 可执行文件路径（跨平台支持）
 */
function getChromePath() {
    const platform = process.platform;

    const paths = {
        darwin: [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
        ],
        win32: [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe',
        ],
        linux: [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/snap/bin/chromium',
        ],
    };

    const candidates = paths[platform] || paths.linux;

    for (const chromePath of candidates) {
        if (chromePath && fs.existsSync(chromePath)) {
            return chromePath;
        }
    }

    // 如果找不到，返回 null，让 Puppeteer 使用内置的 Chromium
    return null;
}

// 解析命令行参数
const args = process.argv.slice(2);
const useNaturalSize = args.includes('--natural');

let inputHtml = null;
let outputPdf = null;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i + 1]) {
        inputHtml = args[i + 1];
        i++;
    } else if (args[i] === '--output' && args[i + 1]) {
        outputPdf = args[i + 1];
        i++;
    } else if (!args[i].startsWith('--')) {
        if (!inputHtml) inputHtml = args[i];
    }
}

// 默认值处理：如果未指定输入文件，尝试查找 ../html 下最新的文件
if (!inputHtml) {
    const htmlDir = path.resolve(__dirname, '../html');
    if (fs.existsSync(htmlDir)) {
        try {
            const files = fs.readdirSync(htmlDir)
                .filter(file => file.endsWith('.html'))
                .map(file => {
                    const fullPath = path.join(htmlDir, file);
                    return { fullPath, mtime: fs.statSync(fullPath).mtime };
                })
                .sort((a, b) => b.mtime - a.mtime); // 按修改时间降序排序

            if (files.length > 0) {
                inputHtml = files[0].fullPath;
                console.log(`未指定输入文件，自动选择最新的文件: ${inputHtml}`);
            }
        } catch (e) {
            console.warn('自动查找最新文件失败:', e.message);
        }
    }
}

inputHtml = inputHtml || 'resume.html';
const resolvedInputPath = path.resolve(process.cwd(), inputHtml);

// 确定输出路径
if (!outputPdf) {
    const inputBaseName = path.basename(resolvedInputPath, path.extname(resolvedInputPath));
    const suffix = useNaturalSize ? '-natural.pdf' : '.pdf';
    // 默认输出到项目根目录下的 pdf 文件夹 (相对于脚本位置 ../pdf)
    const defaultPdfDir = path.resolve(__dirname, '../pdf');
    
    if (!fs.existsSync(defaultPdfDir)) {
        fs.mkdirSync(defaultPdfDir, { recursive: true });
    }
    
    outputPdf = path.join(defaultPdfDir, `${inputBaseName}${suffix}`);
}
const resolvedOutputPath = path.resolve(process.cwd(), outputPdf);

const CONFIG = {
    htmlFile: resolvedInputPath,
    outputFile: resolvedOutputPath,
};

async function generateResumePDF() {
    const chromePath = getChromePath();
    console.log('启动浏览器...');
    if (chromePath) {
        console.log(`使用 Chrome: ${chromePath}`);
    } else {
        console.log('使用 Puppeteer 内置 Chromium');
    }

    const launchOptions = {
        headless: 'new',
    };
    if (chromePath) {
        launchOptions.executablePath = chromePath;
    }

    const browser = await puppeteer.launch(launchOptions);

    const page = await browser.newPage();

    // 加载 HTML 文件
    console.log(`加载文件: ${CONFIG.htmlFile}`);
    await page.goto(`file://${CONFIG.htmlFile}`, {
        waitUntil: 'networkidle0',
        timeout: 30000,
    });

    // 等待字体完全加载
    console.log('等待字体加载...');
    await page.evaluate(() => document.fonts.ready);

    // 等待 Tailwind CSS 和外部资源
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 隐藏打印按钮，并获取页面尺寸
    const pageSize = await page.evaluate(() => {
        // 隐藏打印按钮
        document.querySelectorAll('.no-print').forEach(el => el.style.display = 'none');

        // 获取 .page 元素尺寸
        const pageEl = document.querySelector('.page');
        const rect = pageEl.getBoundingClientRect();

        // 移除 body 的深色背景和阴影
        document.body.style.background = 'white';
        document.body.style.padding = '0';
        document.body.style.margin = '0';
        pageEl.style.boxShadow = 'none';
        pageEl.style.margin = '0';

        return {
            width: rect.width,
            height: rect.height
        };
    });

    console.log(`页面尺寸: ${pageSize.width} x ${pageSize.height}`);

    // 设置视口匹配页面尺寸
    await page.setViewport({
        width: Math.ceil(pageSize.width),
        height: Math.ceil(pageSize.height),
        deviceScaleFactor: 1,
    });

    // 输出 PDF
    const outputPath = CONFIG.outputFile;

    if (useNaturalSize) {
        console.log('模式: 自然尺寸 (矢量 PDF)');
        await page.pdf({
            path: outputPath,
            width: `${pageSize.width}px`,
            height: `${pageSize.height}px`,
            printBackground: true,
            margin: { top: 0, right: 0, bottom: 0, left: 0 },
        });
    } else {
        console.log('模式: A4 缩放 (矢量 PDF)');
        // 计算缩放比例
        const A4_WIDTH_PX = 794;
        const A4_HEIGHT_PX = 1123;
        const scale = Math.min(
            A4_WIDTH_PX / pageSize.width,
            A4_HEIGHT_PX / pageSize.height
        );

        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true,
            margin: { top: 0, right: 0, bottom: 0, left: 0 },
            scale: scale,
        });
    }

    console.log(`PDF 生成成功: ${outputPath}`);

    await browser.close();
    console.log('完成!');
}

generateResumePDF().catch(err => {
    console.error('生成失败:', err);
    process.exit(1);
});
