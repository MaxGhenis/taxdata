import pandas as pd
import numpy as np
import pytest

from extrapolation import Benefits



def test_add_participants():
    """
    Checks
        1. those with benefits still have benefits
        2. record with lowest prob and no benefits gets benefits
    """
    benefit_names = ["medicare"]
    ben = Benefits(benefit_names=benefit_names)

    recid_ext = pd.concat([ben.benefit_extrapolation.RECID for i in range(15)], axis=1)
    recid_ext.columns = list(range(15))
    recid_stack = recid_ext.stack()

    stack_df = Benefits._stack_df(
        WT=ben.WT.loc[:, 'WT2015'] * 0.01,
        I=ben.medicare_participation,
        benefits=ben.medicare_benefits,
        prob=ben.medicare_prob,
        J=15
    )
    stack_df = pd.concat((stack_df, recid_stack), axis=1)

    target = ben.medicare_participant_targets[2015]

    candidates = stack_df.loc[stack_df.I == 0, ].copy()
    for ix in candidates.index.values[:min(100, len(candidates))]:
        assert np.allclose(
            ben.medicare_participation.loc[ix[0], ix[1]],
            np.zeros(1)
        )
    assert candidates.I.sum() == 0
    candidates.loc[:, "I"] = np.ones(len(candidates))
    candidates.loc[:, "I_wt"] = candidates.I * candidates.wt

    noncandidates = stack_df.loc[stack_df.I > 0, ].copy()
    assert noncandidates.I.sum() == len(noncandidates)

    candidates.sort_values("prob", inplace=True, ascending=False)
    noncan_part = noncandidates["I_wt"].sum()
    candidates["cum_participants"] = candidates["I_wt"].cumsum() + noncan_part
    candidates["_diff"] = candidates["cum_participants"] - target
    # # check to make results are close enough
    assert np.allclose(
        candidates[candidates._diff <= 0].cum_participants.max(), target,
        atol=0.0, rtol=0.01
    )

    keeps_benefits = candidates.loc[candidates._diff <= 0, ["prob", "_diff"]]
    loses_benefits = candidates.loc[candidates._diff > 0, ["prob", "_diff"]]

    keep = pd.concat(
        (keeps_benefits.nlargest(10, "prob"),
         keeps_benefits.nsmallest(10, "prob")),
        axis=0
    )
    lose = pd.concat(
        (loses_benefits.nlargest(10, "prob"),
         loses_benefits.nsmallest(10, "prob")),
        axis=0
    )

    for ix in keep.index.values:
        assert np.allclose(
            ben.medicare_participation.loc[ix[0], ix[1]],
            np.zeros(1)
        )
    for ix in lose.index.values:
        assert np.allclose(
            ben.medicare_participation.loc[ix[0], ix[1]],
            np.zeros(1)
        )

    ben.increment_year()

    for ix in keep.index.values:
        assert np.allclose(
            ben.medicare_participation.loc[ix[0], ix[1]],
            np.ones(1)
        )
    for ix in lose.index.values:
        assert np.allclose(
            ben.medicare_participation.loc[ix[0], ix[1]],
            np.zeros(1)
        )


def test_remove_participants():
    """
    Checks
        1. those without benefits still do not have benefits
        2. record with lowest prob and benefits gets no benefits
    """
    benefit_names = ["snap"]
    ben = Benefits(benefit_names=benefit_names)

    recid_ext = pd.concat([ben.benefit_extrapolation.RECID for i in range(15)], axis=1)
    recid_ext.columns = list(range(15))
    recid_stack = recid_ext.stack()

    stack_df = Benefits._stack_df(
        WT=ben.WT.loc[:, 'WT2015'] * 0.01,
        I=ben.snap_participation,
        benefits=ben.snap_benefits,
        prob=ben.snap_prob,
        J=15
    )
    stack_df = pd.concat((stack_df, recid_stack), axis=1)

    target = ben.snap_participant_targets[2015]

    candidates = stack_df.loc[stack_df.I > 0, ].copy()
    for ix in candidates.index.values[:min(100, len(candidates))]:
        assert np.allclose(
            ben.snap_participation.loc[ix[0], ix[1]],
            np.ones(1)
        )

    assert candidates.I.sum() == len(candidates)
    noncandidates = stack_df.loc[stack_df.I == 0, ].copy()
    assert noncandidates.I.sum() == 0

    candidates.sort_values("prob", inplace=True, ascending=False)
    noncan_part = noncandidates["I_wt"].sum()
    candidates["cum_participants"] = candidates["I_wt"].cumsum() + noncan_part
    candidates["_diff"] = candidates["cum_participants"] - target
    # # check to make results are close enough
    assert np.allclose(
        candidates[candidates._diff <= 0].cum_participants.max(), target,
        atol=0.0, rtol=0.01
    )

    keeps_benefits = candidates.loc[candidates._diff <= 0, ["prob", "_diff"]]
    loses_benefits = candidates.loc[candidates._diff > 0, ["prob", "_diff"]]

    keep = pd.concat(
        (keeps_benefits.nlargest(10, "prob"),
         keeps_benefits.nsmallest(10, "prob")),
        axis=0
    )
    lose = pd.concat(
        (loses_benefits.nlargest(10, "prob"),
         loses_benefits.nsmallest(10, "prob")),
        axis=0
    )

    for ix in keep.index.values:
        assert np.allclose(
            ben.snap_participation.loc[ix[0], ix[1]],
            np.ones(1)
        )
    for ix in lose.index.values:
        assert np.allclose(
            ben.snap_participation.loc[ix[0], ix[1]],
            np.ones(1)
        )

    ben.increment_year()

    for ix in keep.index.values:
        assert np.allclose(
            ben.snap_participation.loc[ix[0], ix[1]],
            np.ones(1)
        )
    for ix in lose.index.values:
        assert np.allclose(
            ben.snap_participation.loc[ix[0], ix[1]],
            np.zeros(1)
        )
