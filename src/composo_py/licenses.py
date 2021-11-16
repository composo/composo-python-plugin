import json
from typing import Tuple, Dict, Any

import requests
from requests import ReadTimeout


class SPDXLicensesGetter:

    def __init__(self, cache_folder, sys_interface):
        self.__cache_folder = cache_folder
        self.__sys_interface = sys_interface

    def get(self):
        try:
            content = requests.get(
                f"https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json", timeout=5).text
            self.__sys_interface.write(self.__cache_folder / "licenses.json", content)
        except (ReadTimeout, requests.exceptions.ConnectionError) as e:
            content = self.__sys_interface.read(self.__cache_folder / "licenses.json")
        return json.loads(content)


class LicenseServiceCached:

    def __init__(self, resource_getter, input_interface):
        self.__input_interface = input_interface
        self.__resource_getter = resource_getter

    def get(self, license_id: str) -> Tuple[Dict[str, Any], str]:
        licenses = json.loads(self.__resource_getter.get(
            f"https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"))
        eligible_licenses = {li["licenseId"].strip().lower(): li for li in licenses["licenses"]}

        try:
            choice = eligible_licenses[license_id.lower().strip()]
        except KeyError:
            if not eligible_licenses:
                raise RuntimeError(f"License not found: {license_id}")
            elif len(eligible_licenses) > 1:
                choice = self.__input_interface.choose_from(eligible_licenses)
            else:
                choice = eligible_licenses[0]

        license_text = self.__resource_getter.get(
            f"https://raw.githubusercontent.com/licenses/license-templates/master/templates/{choice['licenseId'].lower()}.txt")

        return choice, license_text


class LicenseService:

    def __init__(self, cache_folder, licenses_getter, input_interface):
        self.__cache_folder = cache_folder
        self.__input_interface = input_interface
        self.__licenses_getter = licenses_getter

    def get(self, license_id: str) -> Tuple[Dict[str, Any], str]:
        licenses = self.__licenses_getter.get()
        eligible_licenses = {li["licenseId"].strip().lower(): li for li in licenses["licenses"]}

        # eligible_licenses = {li["licenseId"]: li for li in licenses["licenses"] if
        #                      license.lower() in li["licenseId"].lower() or license.lower() in li["name"].lower()}
        try:
            choice = eligible_licenses[license_id.lower().strip()]
        except KeyError:
            if not eligible_licenses:
                raise RuntimeError(f"License not found: {license_id}")
            elif len(eligible_licenses) > 1:
                choice = self.__input_interface.choose_from(eligible_licenses)
            else:
                choice = eligible_licenses[0]

        # license_specifier = f"OSI Approved :: {choice['licenseId']} License" if choice["isOsiApproved"] else f"{choice['licenseId']} License"
        # license = requests.get(f"https://raw.githubusercontent.com/spdx/license-list-data/master/text/{choice['licenseId']}.txt").text
        # license = license.replace("YEAR", str(self.__year)) \
        #     .replace("AUTHOR", str(self.__author)) \
        #     .replace("EMAIL", str(self.__email)) \
        #     .replace("<COPYRIGHT HOLDER>", str(self.__author)) \
        license_text = ""
        try:
            license_response = requests.get(
                f"https://raw.githubusercontent.com/licenses/license-templates/master/templates/{choice['licenseId'].lower()}.txt", timeout=5)
            if license_response.status_code == 404:
                nl = "\n"
                # license_text = f"Copyright {self.__year} by {self.__config['author']['name']}{nl}{nl}LICENSE template for {choice['licenseId']} not found, please provide a proper license file"
            else:
                license_text = license_response.text
        except requests.exceptions.ConnectionError as e:
            license_text = f"No license text template found for: {choice['licenseId']}"

        return choice, license_text
