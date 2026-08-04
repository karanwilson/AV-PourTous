function pruneOldPTPS_ERPNextBackups() {
  // CONFIGURATION
  // let folderId = "YOUR_GOOGLE_DRIVE_FOLDER_ID"; // Replace with your exact Backup Folder ID
  let folderId = "1w5d7HwANcBIw508bg5WJNeqWEpedrNmW"; // PTPS Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}

function pruneOldPT_CanteenERPNextBackups() {
  // CONFIGURATION
  let folderId = "1DQDBaLWrUaS2vRs4VnlPuK3PiBh_jKj1"; // PT Canteen Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}

function pruneOldPTDC_ERPNextBackups() {
  // CONFIGURATION
  let folderId = "1QP8KPiTcrbBRnNPCiDe-KuyiLylnSzJR"; // PTDC Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}

function pruneOldAVbakeryERPNextBackups() {
  // CONFIGURATION
  let folderId = "1zg-DGSKqdQQb91JWGWCRVYWb-FFDk0f1"; // AV-Bakery exact Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}

function pruneOldAVbakeryCafeERPNextBackups() {
  // CONFIGURATION
  let folderId = "1NE0ufs5abqZI7G9DeU6QtBU-TvPeNgKv"; // AV-BakeryCafe Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}

function pruneOldAVbakeryCafeTH_ERPNextBackups() {
  // CONFIGURATION
  let folderId = "1XpH1Ng3Rd4XZnlunYBFMZe4RMGsRfxO4"; // TH-AV-BakeryCafe Backup Folder ID
  let daysToKeep = 45; // Change this to your preferred retention period

  let targetFolder = DriveApp.getFolderById(folderId);
  let files = targetFolder.getFiles();
  let cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  Logger.log("Pruning files older than: " + cutoffDate);

  while (files.hasNext()) {
    let file = files.next();
    let fileCreatedDate = file.getDateCreated();

    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}
