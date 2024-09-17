#!/bin/tcsh
# convert a list of labeled coordinates by warping them with AFNI
# 3dNwarpXYZ to a list of spaces
# these go from multiple macaque subects' native space to NMT2_asymm space
# output includes all transformed lists labeled with input and output spaces

# list of input fcsv files with labeled coordinates
# repeating with different directory until we set which one is the correct one
#set indset_dir = "/Users/glend/afids-macaca/data/PHASE2_output_afid_postQC_for_PHASE3"
set indset_dir = "/Users/glend/afids-macaca/data/PHASE2_output_afid_postQC"

set space = NMTv2.0asym

set  subject_warp_dir = ( ~/AFIDS_macaca_data/afids-macaca/afni_aw_subs )

# get subject list
set subs = ( sub-032104 sub-032105 sub-032107 sub-032108 sub-032198 sub-032199 sub-032201 sub-032203 sub-032209 sub-032210 sub-032211 sub-032212 sub-032213 sub-032214 sub-032215 sub-032216 )

# loop over AFIDS coordinate files from each subject
# warp the mean across raters to the NMT2 asymm space
foreach sub ( $subs )
   set dset = ${indset_dir}/${sub}_MEAN.fcsv
   # get file name
   set fn = `@GetAfniPrefix $dset`
   set outprefix = ${sub}_MEAN_in_${space}_final.fcsv

   # forward direction - requires *inverse* according
   # the way 3dNwarpXYZ uses the warp
   # but we have inverse warp here too, so we can use
   # the inverse of the inverse, so no inverting....
   # Still have to use the reverse order on the 
   # inverse affine and inverse warp
   if -e ${subject_warp_dir}/aw_${sub}  then
      set awdir = aw_${sub}
      set invwarp = ""
   else
      echo "Missing warpdir for $sub !!!!"
   endif
   # should probably check for each of the input files, but will let
   # this fail non-gracefully in this case
   set inwarp = "${subject_warp_dir}/$awdir/${sub}_composite_linear_to_template_inv.1D ${subject_warp_dir}/$awdir/${sub}_shft_WARPINV.nii.gz"
 
   # apply the transformation
   # splitting off the affine transformation now because 
   # it consumes vast amounts of memory
   nl_coords_transform.py -infile $dset -inwarp "$inwarp"  \
     -orient LPI -xyzcol_start 1 -prefix $outprefix $invwarp -splitaff
end
