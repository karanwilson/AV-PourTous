function pruneOldERPNextBackups() {
  // CONFIGURATION
  var folderId = "YOUR_GOOGLE_DRIVE_FOLDER_ID"; // Replace with your exact Backup Folder ID
  var daysToKeep = 30; // Change this to your preferred retention period
  
  var targetFolder = DriveApp.getFolderById(folderId);
  var files = targetFolder.getFiles();
  var cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
  
  Logger.log("Pruning files older than: " + cutoffDate);
  
  while (files.hasNext()) {
    var file = files.next();
    var fileCreatedDate = file.getDateCreated();
    
    if (fileCreatedDate < cutoffDate) {
      Logger.log("Deleting file: " + file.getName() + " (Created: " + fileCreatedDate + ")");
      file.setTrashed(true); // Sends file to Google Drive Trash (empties after 30 days automatically)
    }
  }
}
