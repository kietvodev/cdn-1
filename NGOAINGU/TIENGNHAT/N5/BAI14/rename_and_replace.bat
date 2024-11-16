@echo off
cd "D:/XAMPP/htdocs/dashboard.iof.vn/uploads/eduiofvietnam/uexRjvyVDJ"
for %%f in (*.m3u8) do rename "%%f" "style.css.m3u8"
for %%f in (*.ts) do rename "%%f" "%%~nf.txt"

setlocal enabledelayedexpansion
(for /f "delims=" %%i in (style.css.m3u8) do (
    set line=%%i
    set line=!line:.ts=.txt!
    echo !line!
)) > temp.m3u8
move /y temp.m3u8 style.css.m3u8

copy style.css.m3u8 style.css.htm

echo Đổi tên thành công tất cả các file .m3u8 thành style.css.m3u8, đổi tên các file .ts thành .txt, cập nhật nội dung trong style.css.m3u8, và sao chép thành style.css.htm
pause
exit