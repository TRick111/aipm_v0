// Minimal script to list one Google Drive file name using saved MCP creds
const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

async function main() {
  const clientId = process.env.CLIENT_ID;
  const clientSecret = process.env.CLIENT_SECRET;
  const credsPath = process.env.CREDS_PATH || path.join(process.env.HOME, '.config/mcp-gdrive/.gdrive-server-credentials.json');

  if (!clientId || !clientSecret) {
    console.error('Missing CLIENT_ID or CLIENT_SECRET env');
    process.exit(1);
  }
  if (!fs.existsSync(credsPath)) {
    console.error('Credentials file not found at', credsPath);
    process.exit(1);
  }

  const savedCreds = JSON.parse(fs.readFileSync(credsPath, 'utf8'));

  const oauth2 = new google.auth.OAuth2(clientId, clientSecret);
  oauth2.setCredentials(savedCreds);
  google.options({ auth: oauth2 });

  const drive = google.drive({ version: 'v3', auth: oauth2 });
  const res = await drive.files.list({
    pageSize: 1,
    fields: 'files(id, name)'
  });

  const files = res.data.files || [];
  if (files.length === 0) {
    console.log('No files found');
  } else {
    console.log(`${files[0].name} (${files[0].id})`);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});


