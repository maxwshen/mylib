# Colors
red=$'\e[1;31m'
grn=$'\e[1;32m'
yel=$'\e[1;33m'
blu=$'\e[1;34m'
mag=$'\e[1;35m'
cyn=$'\e[1;36m'
end=$'\e[0m'

# Custom prompt with colors
export PS1='\[${cyn}\]\h\[\033[01;34m\]|\[\033[0;32m\]\W\[\033[00m\]\$ '

# Default starting dir
cd /cluster/mshen/

# Redefine cd to also append currdir to log file
function cd() { builtin cd "$@" && echo $(pwd) >> /cluster/mshen/self-library/misc/log.txt; }

# Only write to stdout in a login shell, otherwise scp/sftp breaks
if shopt -q login_shell; then
  printf "\n%s\n" "${yel}==== Recent Directories ====${end}"
  tail -n 5 /cluster/mshen/self-library/misc/log.txt

  printf "\n%s\n" "${red}==== What are you curious about? ====${end}"
  ls
  printf "\n"
fi

# Trim recent directories
tail /cluster/mshen/self-library/misc/log.txt > /cluster/mshen/self-library/misc/log2.txt
mv /cluster/mshen/self-library/misc/log2.txt /cluster/mshen/self-library/misc/log.txt

# Append personal package to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/cluster/mshen/self-library"
