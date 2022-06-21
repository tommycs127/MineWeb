@ECHO OFF
CD /D %~1
TITLE %~2
java -jar .\paperclip-1618.jar
DEL %~3
EXIT