import { copyFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';

// Copy the committed artwork without re-encoding: both sandbox runs emit identical bytes.
await mkdir(outputDir, { recursive: true });
await copyFile(resolve(root, 'entry.png'), resolve(outputDir, 'entry.png'));
