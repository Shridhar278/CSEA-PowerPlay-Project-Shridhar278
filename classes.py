from dataclasses import dataclass

@dataclass
class Team:
    code: str
    name: str
    home_venue: str
    alt_venue: str
    alt_bonus_cr: float

@dataclass
class Config:
    kappa: float
    p_exponent: float
    D0_limit_km: float
    eta: float
    q_exponent: float
    x0_limit_days: float
    delta_0_rust_cr: float
    delta_2_tired_cr: float
    delta_3_cooked_cr: float
    tau_star_days: float
    a_low_cr: float
    a_high_cr: float
    lambda_eq: float
    delta_0_disparity_km: float
    g_multiplier: list[float]