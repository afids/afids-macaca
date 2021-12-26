import os
from matplotlib import pyplot as plt
import nipype.interfaces.ants as ants  # nipype ANTs wrapper
from nilearn import plotting  # Plotting functions from nilearn

code_dir = os.getcwd()
affine_SyN_script = os.path.join(code_dir, "antsRegistration_affine_SyN.sh")
## ALSO make sure that the calls to ants_generate_iterations.py
## within the above script point to the correct path


def register_linear(moving, target, out_basename, transform="Rigid", initialize=0):
    """Linearly registers moving image to target image

    Parameters
    ----------
    moving : str
        path to 3D NIFTI image file
    target : str
        path to 3D NIFTI image file
    out_basename : str
        The basename for the output transforms and transformed images
        e.g. '/path/moving_to_target_'
    transform : str
        'Rigid' (default) or 'Affine'
    initialize: int
        One of {0,1,2}. Initialize the registration at
        0 - geometric centers (default)
        1 - image intensity centers
        2 - image coordinate origins

    Return
    ------
    Linear transformation matrix
        file named as '{out_basename}{transform}_0GenericAffine.mat'
    Transformed image
        moving image transformed into target image space
        file named as: '{out_basename}{transform}_Transformed.nii.gz'
    """
    rgstr = ants.registration.Registration(
        dimension=3,
        float=False,
        fixed_image=target,
        moving_image=moving,
        output_transform_prefix=f"{out_basename}{transform}_",
        output_warped_image=f"{out_basename}{transform}_Transformed.nii.gz",
        initial_moving_transform_com=initialize,
        winsorize_lower_quantile=0.05,
        winsorize_upper_quantile=0.95,
        interpolation="Linear",
        use_histogram_matching=[True],
        transforms=[transform],
        transform_parameters=[(0.1,)],
        metric=["MI"],
        metric_weight=[1],
        radius_or_number_of_bins=[32],
        sampling_strategy=["Regular"],
        sampling_percentage=[0.2],
        number_of_iterations=[[1000, 500, 250]],
        convergence_threshold=[1e-6],
        convergence_window_size=[10],
        shrink_factors=[[8, 4, 2]],
        smoothing_sigmas=[[3, 2, 1]],
        sigma_units=["vox"],
    )

    rgstr.run()


def register_SyN(moving, target, out_basename):
    """Non-linearly registers moving image to target image using ANTs SyN

    Parameters
    ----------
    moving : str
        path to 3D NIFTI image file
    target : str
        path to 3D NIFTI image file
    out_basename : str
        The basename for the output transforms and transformed images
        e.g. '/path/moving_to_target_'

    Return
    ------
    Non-linear forward warp
        file named as {out_basename}SyN_1Warp.nii.gz'
    Non-linear backward warp (inverse of the above)
        file named as '{out_basename}SyN_1InverseWarp.nii.gz'
    Transformed image
        moving image transformed into target image space
        file named as: {out_basename}SyN_Transformed.nii.gz
    """
    rgstr = ants.registration.Registration(
        dimension=3,
        float=False,
        fixed_image=target,
        moving_image=moving,
        output_transform_prefix=f"{out_basename}SyN_",
        output_warped_image=f"{out_basename}SyN_Transformed.nii.gz",
        initial_moving_transform_com=0,
        winsorize_lower_quantile=0.05,
        winsorize_upper_quantile=0.95,
        interpolation="Linear",
        use_histogram_matching=[True],
        transforms=["SyN"],
        transform_parameters=[(0.1,)],
        metric=["CC"],
        metric_weight=[1],
        radius_or_number_of_bins=[4],
        sampling_strategy=["Regular"],
        sampling_percentage=[0.2],
        number_of_iterations=[[500, 200, 50]],
        convergence_threshold=[1e-6],
        convergence_window_size=[10],
        shrink_factors=[[8, 4, 2]],
        smoothing_sigmas=[[3, 2, 1]],
        sigma_units=["vox"],
    )

    rgstr.run()


def combine_transforms(
    moving, target, out_basename, linear_transform, warp, inverse_warp
):

    """
    Combines calculated linear and SyN transforms into 2 composite warps:
    forward (moving_to_target) and backward (target-to-moving).

    Parameters
    ----------
    moving : str
        path to 3D NIFTI image file
    target : str
        path to 3D NIFTI image file
    out_basename : str
        The basename for the output transforms and transformed images
        e.g. '/path/moving_to_target_'
    linear_transform : str
        path to previously calculated linear transform file
        (output of register_linear)
    warp : str
        path to previously calculated non-linear warp
        (output of register_SyN)
    inverse_warp : str
        path to previously calculated non-linear inverse warp
        (output of register_SyN)

    Return
    ------
    Forward composite warp
        File named as '{out_basename}CompositeWarp.nii.gz'
    Backward composite warp
        File named as '{out_basename}InverseCompositeWarp.nii.gz'
    Moving image transformed into target space using the forward warp
        File named as: '{out_basename}_Composite_Transformed.nii.gz'
    Target image transformed into moving space using the backward warp
        File named as: '{out_basename}_InverseComposite_Transformed.nii.gz'
    """

    # Compute the composite warp (func to template)
    # CAUTION: tranforms are applied from last to first (like in linear algebra notation)
    combine1 = ants.ApplyTransforms(
        input_image=moving,
        output_image=f"{out_basename}CompositeWarp.nii.gz",
        reference_image=target,
        transforms=[warp, linear_transform],
        dimension=3,
        print_out_composite_warp_file=True,
    )
    combine1.run()

    # Compute the inverse of the composite warp
    combine2 = ants.ApplyTransforms(
        input_image=target,
        output_image=f"{out_basename}InverseCompositeWarp.nii.gz",
        reference_image=moving,
        transforms=[linear_transform, inverse_warp],
        invert_transform_flags=[True, False],
        dimension=3,
        print_out_composite_warp_file=True,
    )
    combine2.run()

    # transform moving image to target (using forward transform)
    # and target to moving (using backward transform)
    # for checking registration success
    trans1 = ants.ApplyTransforms(
        input_image=moving,
        output_image=f"{out_basename}_Composite_Transformed.nii.gz",
        reference_image=target,
        transforms=f"{out_basename}CompositeWarp.nii.gz",
        dimension=3,
    )
    trans1.run()

    trans2 = ants.ApplyTransforms(
        output_image=f"{out_basename}_InverseComposite_Transformed.nii.gz",
        input_image=target,
        reference_image=moving,
        transforms=f"{out_basename}InverseCompositeWarp.nii.gz",
        dimension=3,
    )
    trans2.run()


def overlay_contours(base, overlay, plot_title="subject-on-template", save_plot=None):
    """Plot for checking registration success.
    Plots base image in ortho slices
    and adds the contours of the overlay image

    Parameters
    ----------
    base : str
        path to 3D NIFTI image file
        e.g. The target image of the registration you want to check
    overlay : str
        path to 3D NIFTI image file
        e.g. The transformed moving image in the target space
    save_plot : str
        Path to the image file to be saved
        e.g. '/path/contour_plot.png'
    """

    display = plotting.plot_anat(
        base, display_mode="ortho", title=plot_title, draw_cross=False, annotate=False
    )
    display.add_contours(overlay)

    if save_plot:
        plt.savefig(save_plot, dpi=128)
        plt.draw()
