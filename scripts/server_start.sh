#!/bin/bash
cd $1
echo -ne "\033]0;$2\007"
java -jar ./paperclip-1618.jar
rm $3
