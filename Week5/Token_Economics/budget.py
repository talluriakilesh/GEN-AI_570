"""
WEEK 5 - Token Economics
Pre-build cost and rate-limit budget planner.

Reads assumptions from .env, estimates daily/monthly token usage and cost,
applies a safety margin to peak RPM/TPM and budget checks, then prints
a planning recommendation.

This is a planning estimate, not a billing guarantee.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)


@dataclass
class FeatureBudget:
    requests_per_day: int
    avg_input_tokens: int
    avg_output_tokens: int
    peak_requests_per_minute: int
    input_price_per_million: float
    output_price_per_million: float
    rpm_limit: int
    tpm_limit: int
    monthly_budget_usd: float
    daily_budget_usd: float
    safety_margin_percent: float

    @classmethod
    def from_env(cls):
        """Build the budget configuration from environment variables."""
        return cls(
            requests_per_day=int(os.getenv("REQUESTS_PER_DAY", "0")),
            avg_input_tokens=int(os.getenv("AVG_INPUT_TOKENS", "0")),
            avg_output_tokens=int(os.getenv("AVG_OUTPUT_TOKENS", "0")),
            peak_requests_per_minute=int(
                os.getenv("PEAK_REQUESTS_PER_MINUTE", "0")
            ),
            input_price_per_million=float(
                os.getenv("INPUT_PRICE_PER_MILLION", "0")
            ),
            output_price_per_million=float(
                os.getenv("OUTPUT_PRICE_PER_MILLION", "0")
            ),
            rpm_limit=int(os.getenv("RPM_LIMIT", "0")),
            tpm_limit=int(os.getenv("TPM_LIMIT", "0")),
            monthly_budget_usd=float(os.getenv("MONTHLY_BUDGET_USD", "0")),
            daily_budget_usd=float(os.getenv("DAILY_BUDGET_USD", "0")),
            safety_margin_percent=float(
                os.getenv("SAFETY_MARGIN_PERCENT", "20")
            ),
        )

    def validate(self):
        """Reject invalid negative assumptions and impossible configuration."""
        non_negative_fields = {
            "requests_per_day": self.requests_per_day,
            "avg_input_tokens": self.avg_input_tokens,
            "avg_output_tokens": self.avg_output_tokens,
            "peak_requests_per_minute": self.peak_requests_per_minute,
            "input_price_per_million": self.input_price_per_million,
            "output_price_per_million": self.output_price_per_million,
            "rpm_limit": self.rpm_limit,
            "tpm_limit": self.tpm_limit,
            "monthly_budget_usd": self.monthly_budget_usd,
            "daily_budget_usd": self.daily_budget_usd,
            "safety_margin_percent": self.safety_margin_percent,
        }
        for field_name, value in non_negative_fields.items():
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.requests_per_day == 0 and self.peak_requests_per_minute > 0:
            # This is not mathematically impossible, but it is often a
            # contradictory planning assumption. Keep it allowed.
            pass

    def calculate(self):
        """Calculate token usage, estimated cost, capacity and budget checks."""
        self.validate()

        input_tokens_day = self.requests_per_day * self.avg_input_tokens
        output_tokens_day = self.requests_per_day * self.avg_output_tokens
        total_tokens_day = input_tokens_day + output_tokens_day

        daily_cost = (
            input_tokens_day * self.input_price_per_million
            + output_tokens_day * self.output_price_per_million
        ) / 1_000_000

        monthly_cost = daily_cost * 30
        margin_multiplier = 1 + self.safety_margin_percent / 100

        peak_rpm_with_margin = (
            self.peak_requests_per_minute * margin_multiplier
        )
        peak_tpm_with_margin = (
            self.peak_requests_per_minute
            * (self.avg_input_tokens + self.avg_output_tokens)
            * margin_multiplier
        )

        return {
            "input_tokens_day": input_tokens_day,
            "output_tokens_day": output_tokens_day,
            "total_tokens_day": total_tokens_day,
            "daily_cost_usd": daily_cost,
            "monthly_cost_usd": monthly_cost,
            "peak_rpm_with_margin": peak_rpm_with_margin,
            "peak_tpm_with_margin": peak_tpm_with_margin,
            "rpm_ok": peak_rpm_with_margin <= self.rpm_limit,
            "tpm_ok": peak_tpm_with_margin <= self.tpm_limit,
            "daily_budget_ok": daily_cost * margin_multiplier
            <= self.daily_budget_usd,
            "monthly_budget_ok": monthly_cost * margin_multiplier
            <= self.monthly_budget_usd,
        }


def print_report(result):
    """Print a readable pre-build budget report."""
    print("\n" + "=" * 48)
    print("TOKEN ECONOMICS REPORT")
    print("=" * 48)
    print(f"Input tokens/day       : {result['input_tokens_day']:,.0f}")
    print(f"Output tokens/day      : {result['output_tokens_day']:,.0f}")
    print(f"Total tokens/day       : {result['total_tokens_day']:,.0f}")
    print(f"Estimated daily cost  : ${result['daily_cost_usd']:.4f}")
    print(f"Estimated monthly cost: ${result['monthly_cost_usd']:.2f}")
    print(f"Peak RPM + margin      : {result['peak_rpm_with_margin']:.1f}")
    print(f"Peak total TPM + margin: {result['peak_tpm_with_margin']:,.0f}")

    checks = {
        "RPM capacity": result["rpm_ok"],
        "TPM capacity": result["tpm_ok"],
        "Daily budget": result["daily_budget_ok"],
        "Monthly budget": result["monthly_budget_ok"],
    }

    print("\nCHECKS")
    for name, passed in checks.items():
        print(f"{name:20}: {'PASS' if passed else 'REVIEW'}")

    if all(checks.values()):
        print("\nRecommendation: WITHIN configured planning limits.")
    else:
        print(
            "\nRecommendation: REVISE assumptions, limits, or design "
            "before build."
        )

    print("\nNote: This is a planning estimate, not a billing guarantee.")
    print("Verify current provider pricing and quota definitions.")
    print("=" * 48)


def main():
    budget = FeatureBudget.from_env()
    result = budget.calculate()
    print_report(result)


if __name__ == "__main__":
    main()
