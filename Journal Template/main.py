import os
import sys
from datetime import date, datetime


class Journal:
	def __init__(self) -> None:
		print("Welcome")
		print(
			"Would you like to create a weekly journal starting from today or a weekly journal starting from a custom date?")
		print("The only correct answers are 'today' or 'custom date'", end="")
		user_input: str = input(": ")
		if user_input.lower() not in ["today", "custom date"]:
			print(f"Unknown option: {user_input}")
			sys.exit(-1)
		else:
			if user_input.lower() == "today":
				Journal.today()
			else:
				Journal.custom_date()

	@staticmethod
	def today() -> None:
		DATETIME_INSTANCE = datetime.now()

		TODAY = DATETIME_INSTANCE.strftime('%A %-d %B %Y')

		FILENAME = Journal.date_setup(DATETIME_INSTANCE)

		print("-" * (len("Creating Weekly Journal  now") + len(FILENAME)))
		print(f"Today is {TODAY}\nCreating Weekly Journal {FILENAME} now")
		print("-" * (len("Creating Weekly Journal  now") + len(FILENAME)))

		Journal.create_file(FILENAME, DATETIME_INSTANCE)

	@staticmethod
	def custom_date() -> None:
		CUSTOM_USER_INPUT: str = input("Input a date in the dd mm yyyy format (e.g. 05 12 2005): ")
		DATETIME_INSTANCE: datetime = datetime.strptime(CUSTOM_USER_INPUT, "%d %m %Y")

		CUSTOM_DATE: str = DATETIME_INSTANCE.strftime('%A %-d %B %Y')
		FILENAME = Journal.date_setup(DATETIME_INSTANCE)

		print("-" * (len("Creating Weekly Journal  now") + len(FILENAME)))
		print(f"The start date is {CUSTOM_DATE}\nCreating Weekly Journal {FILENAME} now")
		print("-" * (len("Creating Weekly Journal  now") + len(FILENAME)))

		Journal.create_file(FILENAME, DATETIME_INSTANCE)

	@staticmethod
	def date_setup(DATETIME_INSTANCE: datetime) -> str:
		NEW_DATE = date.fromtimestamp(DATETIME_INSTANCE.timestamp() + Journal.convert_day_to_seconds(7))

		WEEK_NUMBER: str = DATETIME_INSTANCE.strftime('%U')
		YEAR: str = DATETIME_INSTANCE.strftime('%Y')

		TODAY_FILE_NAME = DATETIME_INSTANCE.strftime('%-d.%-m')
		NEW_DATE_FILE_NAME = NEW_DATE.strftime('%-d.%-m')

		return f"Week {WEEK_NUMBER} of Year {YEAR} ({TODAY_FILE_NAME} - {NEW_DATE_FILE_NAME}).docx"

	@staticmethod
	def create_file(FILENAME: str, DATETIME_INSTANCE: datetime) -> None:
		f = open(FILENAME, "w+")
		for i in range(0, 8):
			Journal_dates = date.fromtimestamp(DATETIME_INSTANCE.timestamp() + Journal.convert_day_to_seconds(i))
			f.write(f"{'-' * 65}\n{Journal_dates.strftime('%A %-d %B %Y')}\n{'-' * 65}")
			f.write("\n" * 46)
		f.close()
		print(Journal.check_if_file_exists(FILENAME))

	@staticmethod
	def convert_day_to_seconds(day: int) -> int:
		return day * 24 * 60 * 60

	@staticmethod
	def check_if_file_exists(file: str) -> str:
		return f"{file} successfully created!!!" if os.path.exists(file) else "Sorry! There was an error! The file " \
																			  "could not be created! "


if __name__ == "__main__":
	Journal()
