import fs from 'fs';
import path from 'path';
import sharp from 'sharp';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const directoryPath = path.join(__dirname, 'public', 'images', 'trip');

async function processImages() {
  const files = fs.readdirSync(directoryPath);
  for (const file of files) {
    if (file.toLowerCase().endsWith('.jpg') || file.toLowerCase().endsWith('.jpeg') || file.toLowerCase().endsWith('.png')) {
      const filePath = path.join(directoryPath, file);
      const tempPath = path.join(directoryPath, `temp_${file}`);
      
      console.log(`Processing ${file}...`);
      try {
        await sharp(filePath)
          .resize(1920, 1080, { fit: 'inside', withoutEnlargement: true })
          .jpeg({ quality: 80, progressive: true })
          .toFile(tempPath);
          
        fs.renameSync(tempPath, filePath);
        console.log(`Finished ${file}. Original replaced.`);
      } catch (e) {
        console.error(`Error processing ${file}:`, e);
      }
    }
  }
}

processImages();
