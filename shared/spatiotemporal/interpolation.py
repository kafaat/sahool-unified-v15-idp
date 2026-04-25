# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Natural cubic-spline resampling — see ADR-011.

Pure-Python implementation (no scipy). The ``natural`` boundary condition
sets the second derivative to zero at both endpoints; outside the input
range we **clamp** to the endpoint values per the ADR-011 boundary policy.
"""

from __future__ import annotations

from datetime import datetime


def _natural_cubic_coeffs(
    xs: list[float], ys: list[float]
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Return ``(a, b, c, d)`` cubic coefficients for each interval.

    For ``i`` in ``[0, n-1)``:
        ``S_i(x) = a_i + b_i*(x - x_i) + c_i*(x - x_i)^2 + d_i*(x - x_i)^3``
    """

    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]

    # Tridiagonal system for the second derivatives (m_i):
    #   h_{i-1} m_{i-1} + 2(h_{i-1}+h_i) m_i + h_i m_{i+1}
    #     = 6 * ((y_{i+1}-y_i)/h_i - (y_i-y_{i-1})/h_{i-1})
    # with m_0 = m_{n-1} = 0 (natural).
    alpha = [0.0] * n
    for i in range(1, n - 1):
        alpha[i] = 3.0 * (
            (ys[i + 1] - ys[i]) / h[i] - (ys[i] - ys[i - 1]) / h[i - 1]
        )

    # Thomas algorithm for the symmetric tridiagonal system.
    l = [1.0] + [0.0] * (n - 1)  # noqa: E741 - matches Numerical Recipes notation
    mu = [0.0] * n
    z = [0.0] * n
    for i in range(1, n - 1):
        l[i] = 2.0 * (xs[i + 1] - xs[i - 1]) - h[i - 1] * mu[i - 1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]
    l[n - 1] = 1.0
    z[n - 1] = 0.0

    c = [0.0] * n
    b = [0.0] * (n - 1)
    d = [0.0] * (n - 1)
    a = ys[:-1]
    for j in range(n - 2, -1, -1):
        c[j] = z[j] - mu[j] * c[j + 1]
        b[j] = (ys[j + 1] - ys[j]) / h[j] - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0
        d[j] = (c[j + 1] - c[j]) / (3.0 * h[j])
    return a, b, c[:-1], d


def resample_cubic(
    timestamps: list[datetime],
    values: list[float],
    target_timestamps: list[datetime],
) -> list[float]:
    """Resample irregular series onto ``target_timestamps`` via cubic spline.

    Boundary policy: clamp at endpoints. Requires at least two anchor points;
    with exactly two points the result is linear interpolation.
    """

    if len(timestamps) != len(values):
        raise ValueError("timestamps and values must have the same length")
    if len(timestamps) < 2:
        raise ValueError("at least two anchor points are required")
    # Reject unsorted / duplicated timestamps — ambiguous for spline fitting.
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i - 1]:
            raise ValueError("timestamps must be strictly increasing")

    epoch = timestamps[0]
    xs = [(t - epoch).total_seconds() for t in timestamps]
    ys = list(values)

    if len(xs) == 2:
        # Linear shortcut — natural cubic with two points degenerates anyway.
        x0, x1 = xs
        y0, y1 = ys
        slope = (y1 - y0) / (x1 - x0)
        out: list[float] = []
        for t in target_timestamps:
            x = (t - epoch).total_seconds()
            if x <= x0:
                out.append(y0)
            elif x >= x1:
                out.append(y1)
            else:
                out.append(y0 + slope * (x - x0))
        return out

    a, b, c, d = _natural_cubic_coeffs(xs, ys)

    out2: list[float] = []
    for t in target_timestamps:
        x = (t - epoch).total_seconds()
        if x <= xs[0]:
            out2.append(ys[0])
            continue
        if x >= xs[-1]:
            out2.append(ys[-1])
            continue
        # Locate the interval via binary search.
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        dx = x - xs[lo]
        out2.append(a[lo] + b[lo] * dx + c[lo] * dx * dx + d[lo] * dx * dx * dx)
    return out2
