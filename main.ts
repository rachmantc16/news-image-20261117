// News-image entry (Node 22, standard library only): the entry image is the
// entry.png beside this file. Before handing it over, the program validates
// that image against the competition's format gate — a real PNG, at most
// 1 MiB, at most 1024 by 1024 pixels — and only then copies it to
// /output/entry.png. An invalid image fails loudly instead of being handed
// over and rejected by the gate.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576; // 1 MiB
const MAX_PIXELS = 1024;

const sourcePath = fileURLToPath(new URL('./entry.png', import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputPath = join(outputDir, 'entry.png');

const bytes = readFileSync(sourcePath);

if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
if (bytes.length < 24 || !bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
  throw new Error('entry.png is not a PNG file (bad signature)');
}
if (bytes.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk where one is expected');
}
// A complete PNG ends with the 12-byte IEND trailer; a truncated file that
// still has a valid header must not be handed over.
const IEND_TRAILER = Buffer.from([
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);
if (!bytes.subarray(bytes.length - 12).equals(IEND_TRAILER)) {
  throw new Error('entry.png is truncated (no IEND trailer at the end)');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width === 0 || height === 0 || width > MAX_PIXELS || height > MAX_PIXELS) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourcePath, outputPath);

console.log(
  `validated entry.png: PNG ${width}x${height}, ${bytes.length} bytes ` +
  `(${(bytes.length / 1024).toFixed(1)} KiB) — copied to ${outputPath}`,
);
