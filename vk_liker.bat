:Loop
set LikeCnt=15

for %%f in ("login;password") DO @(
ping 8.8.8.8 -n 1 | find /i "TTL=" && (python.exe vk_liker.py %%f %LikeCnt%) || (echo %date% %time% No Internet!)
) 

echo Wait 1 hrs
python.exe timeout.py 1

goto :Loop

pause