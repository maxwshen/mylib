# For Broad servers

# Permissions
umask 002

############################################################
# Path
############################################################
PATH=$HOME/bin:$PATH
# added by Miniconda3 installer
export PATH="/home/unix/maxwshen/miniconda3/bin:$PATH"
# PATH=/home/unix/maxwshen/venv/bin:$PATH
# PYTHONPATH=/home/unix/maxwshen/.local/lib/python3.4/site-packages/

############################################################
# Use and aliases
############################################################
# use -a Python-2.7
# use -a Python-3.4
# use -a R-3.2
# Hide stdout
use -a prompt1 > /dev/null
use -a UGER > /dev/null
# alias python=python3.7
# alias python="/broad/software/free/Linux/redhat_6_x86_64/pkgs/python_2.7.1-sqlite3-rtrees/bin/python2.7"
# export PYTHONPATH=/broad/compbio/maxwshen/venv/lib/python2.7/site-packages:PYTHONPATH

############################################################
# Interactive shell login
############################################################
# alias qrshx=qrsh -now n -l h_rt=12:00:00,h_vmem=8G
# ish
if shopt -q login_shell; then
  if [ "$HOSTNAME" = "gold.broadinstitute.org" ] || [ "$HOSTNAME" = "silver.broadinstitute.org" ] || [ "$HOSTNAME" = "platinum.broadinstitute.org" ] || [ "$HOSTNAME" = "silver" ] || [ "$HOSTNAME" = "platinum" ]; then
    printf "Requesting interactive login shell: qrsh -now n -l h_rt=12:00:00,h_vmem=8G\n"
    qrsh -now n -l h_rt=12:00:00,h_vmem=8G

  else

    ############################################################
    # Custom prompts with colors
    ############################################################
    red=$'\e[1;31m'
    grn=$'\e[1;32m'
    yel=$'\e[1;33m'
    blu=$'\e[1;34m'
    mag=$'\e[1;35m'
    cyn=$'\e[1;36m'
    end=$'\e[0m'
    export PS1='\[${cyn}\]\h\[\033[01;34m\]|\[\033[0;32m\]\W\[\033[00m\]\$ '

    ############################################################
    # Default dir
    ############################################################
    cd /ahg/regevdata/projects/E3PerturbSeq/181024_Max_Rotation/

    ############################################################
    # Log and display recent directories
    ############################################################
    if [[ "x$RUN_ONCE_MY" == "x" ]]; then
      export RUN_ONCE_MY="1"
      function cd() { builtin cd "$@" && echo $(pwd) >> /home/unix/maxwshen/.dir.log; }

      # Remove duplicates
      awk '!seen[$0]++' /home/unix/maxwshen/.dir.log > /home/unix/maxwshen/.dir.2.log
      mv /home/unix/maxwshen/.dir.2.log /home/unix/maxwshen/.dir.log

      # Remove default starting directory. $ matches end-of-line
      echo "$(grep -v "/ahg/regevdata/projects/E3PerturbSeq/181024_Max_Rotation$" /home/unix/maxwshen/.dir.log)" > /home/unix/maxwshen/.dir.log

      printf "\n%s\n" "${yel}==== Recent Directories ====${end}"
      tail -n 12 /home/unix/maxwshen/.dir.log
      printf "\n"

      tail -n 8 /home/unix/maxwshen/.dir.log > /home/unix/maxwshen/.dir.2.log
      mv /home/unix/maxwshen/.dir.2.log /home/unix/maxwshen/.dir.log
    fi
  fi
fi
