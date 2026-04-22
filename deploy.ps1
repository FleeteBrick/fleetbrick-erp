$git = "C:\Users\RobsonCostadeSouza\AppData\Local\git-portable\cmd\git.exe"
& $git add -A
& $git commit -m "Initial commit"
& $git branch -M main
& $git remote add origin https://github.com/fleetebrick-2501/fleetbrick-erp.git
& $git push -u origin main