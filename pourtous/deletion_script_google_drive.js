function pruneOldERPNextBackups() {
  // CONFIGURATION
  let folderId = "YOUR_GOOGLE_DRIVE_FOLDER_ID"; // Replace with your exact Backup Folder ID
  let daysToKeep = 30; // Change this to your preferred retention period

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
