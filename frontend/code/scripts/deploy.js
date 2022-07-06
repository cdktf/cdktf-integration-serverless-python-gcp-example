const path = require('path');
const {Storage} = require('@google-cloud/storage');
const execSync = require('child_process').execSync;

// read env from .env.production.local (cdktf writes outputs into this file)
const { error } = require('dotenv').config({path: path.resolve(__dirname, '..', '.env.production.local')});
if (error) {
    throw error;
} 
// The ID of your GCS bucket
const bucketName = "$BUCKET_NAME";

// The path to your file to upload
const filePath = './build';

// The new ID for your GCS file
const destFileName = 'static-site';

const storage = new Storage();

async function uploadFile() {
    await storage.bucket(bucketName).upload(filePath, {
      destination: destFileName,
    });
  
    console.log(`${filePath} uploaded to ${bucketName}`);
  }
  
//uploadFile().catch(console.error);

execSync("gsutil rsync -R build/ gs://$BUCKET_NAME")

