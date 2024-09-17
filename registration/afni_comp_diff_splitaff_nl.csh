#!/bin/tcsh
# afni_comp_diff_splitaff_nl.csh
# compute differences among coordinates computed for each subject
# comparing affine vs affine+nonlinear
# and affine+nonlinear with split computation (affine, then nonlinear)
# vs combined affine+nonlinear
#
# one subject (032014) had large translation that used up memory and
# didn't work with usual combined transformation
# split computation uses less memory and works for all subjects.
# This checks to see differences between the two methods
#
# results show about +/-2mm difference maximum between affine, affine+nonlinear
# and 0.001mm (1 micron) for the two-step computation of affine+nonlinear vs
# the 1-step

set subs = ( sub-032104 sub-032105 sub-032107 sub-032108 sub-032198 sub-032199 sub-032201 sub-032203 sub-032209 sub-032210 sub-032211 sub-032212 sub-032213 sub-032214 sub-032215 sub-032216 )

# make summary table for differences between splitting the warp into two steps
# (Vecwarp+3dNwarpXYZ) vs the combined single step in 3dNwarpXYZ
# verifies little difference between two methods (at around 1 micron max)
echo "#difference between nonlinear and affine coordinates" > split_diffsumm.1D
echo "#sub    min    max   mean   stdev" >> split_diffsumm.1D
foreach sub ( $subs )
   set ff = xformxyzout_${sub}_MEAN_in_NMTv2.0asym_final.1D
   3dcalc -a "${ff}"\'  -b "temp_noaffine/${ff}"\' \
     -expr 'a-b' -prefix tempdiff_${sub}.1D
   set ssd = `3dBrickStat -min -max -mean -stdev -slow tempdiff_${sub}.1D`
   echo $sub $ssd >> split_diffsumm.1D
end

# make summary table for differences between nonlinear and affine coordinates
echo "#difference between nonlinear and affine coordinates" > aff_diffsumm.1D
echo "#sub    min    max   mean   stdev" >> aff_diffsumm.1D
foreach sub ( $subs )
   set ff = xformxyzout_${sub}_MEAN_in_NMTv2.0asym_final.1D
   set ff_aff =  xformxyzout_${sub}_MEAN_in_NMTv2.0asym_final_aff.1D
   3dcalc -a "${ff}"\'  -b "${ff_aff}"\' \
     -expr 'a-b' -prefix tempdiff_aff_${sub}.1D
   set ssd = `3dBrickStat -min -max -mean -stdev -slow tempdiff_aff_${sub}.1D`
   echo $sub $ssd >> aff_diffsumm.1D
end
