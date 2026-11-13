const http = require('http');
const { spawn } = require('child_process');
const readline = require('readline');

const PORT = process.env.PORT || 5000;
const HOST = '127.0.0.1';

console.log('[Server] Starting Python Flask backend worker...');
const py = spawn('python', ['-u', 'worker.py'], {
    cwd: __dirname,
    env: process.env,
    stdio: ['pipe', 'pipe', 'inherit']
});

const rl = readline.createInterface({
    input: py.stdout,
    crlfDelay: Infinity
});

let isReady = false;
const queue = [];

rl.on('line', (line) => {
    if (line === 'READY') {
        isReady = true;
        console.log('[Server] Python Flask backend is ready and connected.');
        return;
    }

    if (queue.length > 0) {
        const { res } = queue.shift();
        try {
            const data = JSON.parse(line);
            const body = Buffer.from(data.body_b64, 'base64');
            res.writeHead(data.status, data.headers);
            res.end(body);
        } catch (err) {
            console.error('[Server] Response parse error:', err);
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Server internal error');
        }
    }
});

py.on('close', (code) => {
    console.error(`[Server] Python backend exited with code ${code}`);
    process.exit(code || 1);
});

const server = http.createServer((req, res) => {
    let chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
        const bodyStr = Buffer.concat(chunks).toString('utf-8');
        const reqPayload = {
            method: req.method,
            path: req.url,
            headers: req.headers,
            body: bodyStr
        };

        queue.push({ res });
        py.stdin.write(JSON.stringify(reqPayload) + '\n');
    });
});

server.listen(PORT, HOST, () => {
    console.log(`==================================================`);
    console.log(`Neighborhood Helper is running!`);
    console.log(`Local URL: http://${HOST}:${PORT}`);
    console.log(`Subtitle: Local Services. Trusted Helpers. Simple Booking.`);
    console.log(`Database: MySQL 8.0 connected`);
    console.log(`==================================================`);
});
