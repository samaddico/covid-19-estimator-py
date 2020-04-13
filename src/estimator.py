def estimator(data):

    infected = data.get("reportedCases") * 10
    severely_infected = data.get("reportedCases") * 50

    infections_per_time = __get_infections_by_requested_time(
        infected=infected,
        period_type=data.get("periodType"),
        time_to_elapse=data.get("timeToElapse")
    )

    severe_infections_per_time = __get_infections_by_requested_time(
        infected=severely_infected,
        period_type=data.get("periodType"),
        time_to_elapse=data.get("timeToElapse")
    )

    cases = int(infections_per_time * 0.15)
    severe_cases = int(severe_infections_per_time * 0.15)

    available_beds_for_cases = __get_available_hospital_beds(
        data.get("totalHospitalBeds"),
        cases
    )

    available_beds_for_severe_cases = __get_available_hospital_beds(
        data.get("totalHospitalBeds"),
        severe_cases
    )

    icu_cases = 0.05 * infections_per_time
    severe_icu_cases = 0.05 * severe_infections_per_time

    cases_ventilators = 0.02 * infections_per_time
    severe_cases_ventilators = 0.02 * severe_infections_per_time

    dollar_in_flight = __get_money_loss(
        percentage=data.get("region").get("avgDailyIncomePopulation"),
        avg_income=data.get("region").get("avgDailyIncomeInUSD"),
        days=__get_period_duration(data.get("periodType"), data.get("timeToElapse")),
        infections=infections_per_time
    )

    dollar_in_flight_severe = __get_money_loss(
        percentage=data.get("region").get("avgDailyIncomePopulation"),
        avg_income=data.get("region").get("avgDailyIncomeInUSD"),
        days=__get_period_duration(data.get("periodType"), data.get("timeToElapse")),
        infections=severe_infections_per_time
    )

    # build output objects
    impact = {
        "currentlyInfected": infected,
        "infectionsByRequestedTime": infections_per_time,
        "severeCasesByRequestedTime": cases,
        "hospitalBedsByRequestedTime": available_beds_for_cases,
        "casesForICUByRequestedTime": icu_cases,
        "casesForVentilatorsByRequestedTime": cases_ventilators,
        "dollarsInFlight": dollar_in_flight
    }

    severe_impact = {
        "currentlyInfected": severely_infected,
        "infectionsByRequestedTime": severe_infections_per_time,
        "severeCasesByRequestedTime": severe_cases,
        "hospitalBedsByRequestedTime": available_beds_for_severe_cases,
        "casesForICUByRequestedTime": severe_icu_cases,
        "casesForVentilatorsByRequestedTime": severe_cases_ventilators,
        "dollarsInFlight": dollar_in_flight_severe
    }

    result = {
        "data": data,
        "impact": impact,
        "severeImpact": severe_impact
    }

    return result


def __get_period_duration(period_type, time_to_elapse):
    """
    Converts all periods to unit of days.

    :param period_type: the period type to use, possible values : months, weeks, days.
    :param time_to_elapse: the duration in numbers.
    :return: an integer representing duration in days.
    """
    switcher = {
        "months": 30 * time_to_elapse,
        "weeks": 7 * time_to_elapse,
        "days": time_to_elapse,
    }
    return switcher.get(period_type.lower(), "Invalid period type")


def __get_infections_by_requested_time(infected, period_type, time_to_elapse):
    """
    Calculates the number of infections by per time.

    :param infected: number of people currently affected.
    :param period_type: the unit of `time_to_elapse`.
    :param time_to_elapse: the duration of infection.
    :return: the number of infection by per time.
    """
    duration = int(__get_period_duration(period_type, time_to_elapse) / 3)
    return infected * pow(2, duration)


def __get_available_hospital_beds(beds_count, cases):
    """
    Compute the number of available beds given the number of cases.

    :param beds_count: number of hospital beds.
    :param cases: the number of cases.
    :return: number of available beds.
    """
    available_beds = 0.35 * beds_count
    return int(available_beds - cases)


def __get_money_loss(percentage, avg_income, days, infections):
    """
    Calculates money to be losed in the economy.

    :param percentage: percentage of populaton that earn `avg_income`.
    :param avg_income: the average income of infected.
    :param days: period of infection.
    :param infections: number of infectionds per time.
    :return: the amount lossed per infections.
    """
    return infections * percentage * avg_income * days
