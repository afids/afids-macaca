#!/bin/tcsh
# AFIDS_align_subjects_afni.csh
# align all individual subjects to NMT2.0 asymm template

# template location (skullstripped NMT2 asymm - full head FOV)
set template =  ~/NMT_v2.0_asym/NMT_v2.0_asym_fh/NMT_v2.0_asym_fh_SS.nii.gz

# subject dir
set subject_dir = ~/AFIDS_macaca_data/single_macaca

# goto REDO
# subjects to process
set subs = ( ${subject_dir}/sub*T1w.nii.gz)

foreach sub ( $subs )
   # use short subject name before the underscore
   set subname = `@GetAfniPrefix $sub |awk -F_ '{print $1}'`
   @animal_warper -base $template -base_abbrev NMT2 \
      -input $sub -input_abbrev $subname \
      -outdir aw_${subname} -ok_to_exist
end

exit

REDO:
# all except sub sub-032215 warped well
# try masking with premade mask
set subs_REDO = ( ${subject_dir}/sub-032215*T1w.nii.gz )
set subs_REDO = ( ./sub-032215_ab.nii.gz )
set maskdir = "~/AFIDS_macaca_data/single_macaca/brainmasks"
foreach sub ( $subs_REDO )
   # use short subject name before the underscore
   set subname = `@GetAfniPrefix $sub |awk -F_ '{print $1}'`
   set mask = ${maskdir}/${subname}*brainmask.nii.gz
   set aw_dir =  aw_${subname}_REDO7
   mkdir -p $aw_dir
   # mask and rescale to short integers
   #3dcalc -a $sub -b $mask -expr '10*a*step(b)' -datum short -nscale \
      #-prefix $aw_dir/${subname}.nii.gz
   ## pad to a smaller box around the dataset
   #3dAutobox -npad 10 -prefix $aw_dir/${subname}_ab.nii.gz  \
      #$aw_dir/${subname}.nii.gz
   ## align center separately just for testing
   #@Align_Centers -base $template  -dset $aw_dir/${subname}_ab.nii.gz -no_cp
   # try with maxlev 4 to save time
#      -input  $aw_dir/${subname}_ab.nii.gz -input_abbrev $subname \
   @animal_warper -base $template -base_abbrev NMT2 \
      -input  $sub -input_abbrev $subname \
      -outdir $aw_dir -ok_to_exist -cost nmi -maxlev 4 -supersize \
      -align_centers_meth OFF -align_type affine
end
