#!/bin/tcsh
# convert a list of labeled coordinates by warping them with AFNI
# 3dNwarpXYZ to a list of spaces
# these all go from one input template space for macaques to another
# output includes all transformed lists labeled with input and output spaces

# list of input fcsv files with labeled coordinates
set indsets = ( \
  ~/AFIDS_macaca_data/afids-macaca/data/PHASE0_output_afid/nmtv1.3_MEAN.fcsv \
  ~/AFIDS_macaca_data/afids-macaca/data/PHASE0_output_afid/d99_MEAN.fcsv \
  ~/AFIDS_macaca_data/afids-macaca/data/PHASE0_output_afid/macaqueMNI_MEAN.fcsv \
  ~/AFIDS_macaca_data/afids-macaca/data/PHASE0_output_afid/yerkes19_MEAN.fcsv \
  ~/AFIDS_macaca_data/afids-macaca/data/PHASE0_output_afid/inia19_MEAN.fcsv \
)

# make list to match the datasets above
set dsetspacelist = ( NMTv1.3 D99 MNImac Yerkes19 inia19 )

set spacelist = ( NMTv1.3 NMTv2sym NMTv2asym  D99 MNImac Yerkes19 inia19 )

set  template_warp_dir = ~/AFIDS_templates/AFIDS_afni_warps

set dseti = 1
foreach dset ( $indsets )
   # get file name
   set fn = `@GetAfniPrefix $dset`

   # get base space
   set base_space = ${dsetspacelist[$dseti]} 

   # transform to all spaces using AFNI-computed transforms
   foreach space ( $spacelist )
      # check if no transform needed
      if ($space == $base_space) then
         continue
      endif
      set outprefix = ${base_space}_to_${space}_MEAN.fcsv

      # find warp between the spaces
      # try forward direction - requires *inverse* according
      # the way 3dNwarpXYZ uses the warp
      if -e ${template_warp_dir}/aw_${base_space}_to_${space}  then
         set awdir = aw_${base_space}_to_${space}
         set invwarp = "-invwarp"
         set inspace = $base_space
      # uses warp without inverting (see 3dNwarpXYZ -help)
      else
         set awdir = aw_${space}_to_${base_space}
         set invwarp = ""
         set inspace = $space
      endif

      set inwarp = "${template_warp_dir}/$awdir/${inspace}_shft_WARP.nii.gz ${template_warp_dir}/$awdir/${inspace}_composite_linear_to_template.1D"

      # apply the transformation
      nl_coords_transform.py -infile $dset -inwarp "$inwarp"  \
        -orient LPI -xyzcol_start 1 -prefix $outprefix $invwarp -slowinv
   end
   # advance to next space of input dataset
   @ dseti ++ 
end
