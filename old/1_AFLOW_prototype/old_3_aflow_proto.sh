#!/bin/bash
########################################################
# THIS SHOULD BE COPIED INTO THE comparison* DIRECTORY #
# also pay attention to the --misfit_* settings        #
# --add_matching_aflow_prototypes can cause errors     #
# --> better to do it separately                       #
########################################################

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
        exit
fi

### CONSTANTS ##########################################
match=1.0
options="-D $1 --np=7 --primitive --ignore_decorations --misfit_match=$match --misfit_family=$match --ignore_local_geometry --add_aflow_prototype_designation --print_mapping"
echo "Match misfit level = $match"
########################################################

datetime=`date +"%Y-%m-%d-%T"`

outdir=comparison-output_"$match"_"$datetime"
logfile=log_3_compare.log

start=$(date +%s)

echo -e "OPTIONS:" > $logfile
echo $options >> $logfile
echo -e "\nOUTPUT:" >> $logfile
aflow --compare_structures $options >> $logfile
end=$(date +%s)
elapsed=$(( end - start ))
eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')" >> $logfile

mkdir $outdir
cp "$1"/structure_* $outdir
#cp "$1"/duplica* $outdir
cp $logfile $outdir
