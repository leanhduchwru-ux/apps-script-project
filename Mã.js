// Tên trang tính lưu trữ công văn
const SHEET_NAME = "Danh sách Công văn";
const COMPANY_SHEET_NAME = "Công văn của công ty";
const FOLDER_NAME = "Công văn Đính kèm";

/**
 * Điều hướng người dùng đến giao diện Web App
 */
function doGet() {
  return HtmlService.createTemplateFromFile("Giao-dien")
    .evaluate()
    .setTitle("Hệ thống Nhập Công văn")
    .setSandboxMode(HtmlService.SandboxMode.IFRAME)
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Lấy hoặc tạo Google Sheet để lưu trữ dữ liệu công văn
 */
function getOrCreateSheet() {
  const files = DriveApp.getFilesByName("Quản lý Công văn");
  let ss;
  if (files.hasNext()) {
    const file = files.next();
    ss = SpreadsheetApp.openById(file.getId());
  } else {
    ss = SpreadsheetApp.create("Quản lý Công văn");
  }
  
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    // Tạo tiêu đề cột nếu trang tính mới được tạo
    const headers = [
      "STT", 
      "Thời gian nhập", 
      "Số/Ký hiệu", 
      "Ngày ban hành", 
      "Ngày nhận", 
      "Loại văn bản", 
      "Cơ quan ban hành", 
      "Trích yếu", 
      "Nơi nhận / Người xử lý", 
      "Liên kết tệp đính kèm",
      "Công văn liên kết"
    ];
    sheet.appendRow(headers);
    // Định dạng tiêu đề
    const range = sheet.getRange(1, 1, 1, headers.length);
    range.setFontWeight("bold");
    range.setBackground("#2c3e50");
    range.setFontColor("#ffffff");
    range.setHorizontalAlignment("center");
    sheet.setFrozenRows(1);
  }

  // Tự động kiểm tra và tạo trang tính "Công văn của công ty" ngay sau sheet đầu tiên
  let companySheet = ss.getSheetByName(COMPANY_SHEET_NAME);
  if (!companySheet) {
    const sheetIndex = sheet.getIndex();
    companySheet = ss.insertSheet(COMPANY_SHEET_NAME, sheetIndex); // Chèn vào ngay sau sheet Danh sách Công văn
    
    const headers = [
      "STT", 
      "Thời gian nhập", 
      "Số/Ký hiệu", 
      "Ngày ban hành", 
      "Ngày nhận", 
      "Loại văn bản", 
      "Cơ quan ban hành", 
      "Trích yếu", 
      "Nơi nhận / Người xử lý", 
      "Liên kết tệp đính kèm",
      "Công văn liên kết"
    ];
    companySheet.appendRow(headers);
    
    // Định dạng tiêu đề cho sheet Công văn của công ty
    const range = companySheet.getRange(1, 1, 1, headers.length);
    range.setFontWeight("bold");
    range.setBackground("#34495e"); // Tông màu xám đậm sang trọng khác biệt một chút
    range.setFontColor("#ffffff");
    range.setHorizontalAlignment("center");
    companySheet.setFrozenRows(1);
  }
  
  return sheet;
}

/**
 * Lấy danh sách công văn từ sheet "Công văn của công ty" để điền vào dropdown liên kết
 */
function getCompanyDocuments() {
  try {
    const files = DriveApp.getFilesByName("Quản lý Công văn");
    if (!files.hasNext()) return [];
    const ss = SpreadsheetApp.openById(files.next().getId());
    const sheet = ss.getSheetByName(COMPANY_SHEET_NAME);
    if (!sheet) return [];
    
    const lastRow = sheet.getLastRow();
    if (lastRow <= 1) return [];
    
    // Đọc cột Số/Ký hiệu (Cột C - 3) và Trích yếu (Cột H - 8)
    const values = sheet.getRange(2, 1, lastRow - 1, 11).getValues();
    return values.map(row => {
      return {
        docNumber: row[2], // Cột C (Số/Ký hiệu)
        summary: row[7]    // Cột H (Trích yếu)
      };
    }).filter(item => item.docNumber && item.docNumber.toString().trim() !== "");
  } catch (error) {
    return [];
  }
}

/**
 * Lấy hoặc tạo thư mục trên Google Drive để lưu tệp đính kèm
 */
function getOrCreateFolder() {
  const folders = DriveApp.getFoldersByName(FOLDER_NAME);
  if (folders.hasNext()) {
    return folders.next();
  }
  return DriveApp.createFolder(FOLDER_NAME);
}

/**
 * Hàm lưu trữ thông tin công văn và tệp đính kèm
 * @param {Object} data Đối tượng chứa thông tin công văn từ Client
 */
function submitDocument(data) {
  try {
    let fileUrl = "";
    
    // Xử lý lưu tệp đính kèm lên Drive nếu có
    if (data.fileData && data.fileName) {
      const folder = getOrCreateFolder();
      const rawData = Utilities.base64Decode(data.fileData.split(",")[1]);
      const blob = Utilities.newBlob(rawData, data.fileType, data.fileName);
      const file = folder.createFile(blob);
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      fileUrl = file.getUrl();
    }
    
    // Đảm bảo các sheet và folder đã được tạo lập
    getOrCreateSheet();
    
    // Mở bảng tính và chọn đúng sheet đích
    const files = DriveApp.getFilesByName("Quản lý Công văn");
    let ss;
    if (files.hasNext()) {
      ss = SpreadsheetApp.openById(files.next().getId());
    } else {
      ss = SpreadsheetApp.create("Quản lý Công văn");
    }
    
    const targetSheetName = data.targetSheet || SHEET_NAME;
    const sheet = ss.getSheetByName(targetSheetName) || ss.insertSheet(targetSheetName);
    
    const lastRow = sheet.getLastRow();
    const stt = lastRow === 1 ? 1 : lastRow; // Tính số thứ tự
    
    // Tìm kiếm và thiết lập công thức HYPERLINK liên kết sang dòng tương ứng trong sheet Công văn của công ty
    let linkedDocValue = data.linkedDoc || "";
    if (data.linkedDoc && targetSheetName === SHEET_NAME) {
      const companySheet = ss.getSheetByName(COMPANY_SHEET_NAME);
      if (companySheet) {
        const companyGid = companySheet.getSheetId();
        const lastCompanyRow = companySheet.getLastRow();
        if (lastCompanyRow > 1) {
          // Đọc toàn bộ cột C (Số/Ký hiệu) của sheet Công văn của công ty
          const companyNumbers = companySheet.getRange(1, 3, lastCompanyRow, 1).getValues();
          let matchedRow = -1;
          for (let i = 0; i < companyNumbers.length; i++) {
            if (companyNumbers[i][0].toString().trim() === data.linkedDoc.toString().trim()) {
              matchedRow = i + 1; // Vì index mảng 0-based còn hàng Sheet là 1-based
              break;
            }
          }
          if (matchedRow !== -1) {
            // Tạo công thức HYPERLINK trỏ trực tiếp đến ô Số/Ký hiệu của dòng đã tìm thấy
            linkedDocValue = `=HYPERLINK("#gid=${companyGid}&range=C${matchedRow}", "${data.linkedDoc}")`;
          }
        }
      }
    }
    
    const rowData = [
      stt,
      new Date(), // Thời gian nhập
      data.docNumber,
      data.publishDate,
      data.receiveDate,
      data.docType,
      data.issuer,
      data.summary,
      data.receiver,
      fileUrl,
      linkedDocValue // Sử dụng công thức link nếu có
    ];
    
    sheet.appendRow(rowData);
    return {
      success: true,
      message: "Lưu công văn thành công!",
      sheetUrl: ss.getUrl()
    };
  } catch (error) {
    return {
      success: false,
      message: "Có lỗi xảy ra: " + error.toString()
    };
  }
}
