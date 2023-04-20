# TODO #214 work on how the training Data is created and used
from django.core.management.base import BaseCommand
from nadooit_website.models import Session, Session_Signal


def prepare_session_data():
    sessions = Session.objects.all()
    session_data = []

    for session in sessions:
        signals = Session_Signal.objects.filter(session=session)
        signal_types = [signal.session_signal_type for signal in signals]
        signal_type_ids = [hash(signal_type) % 1000 for signal_type in signal_types]
        session_data.append(signal_type_ids)

    return session_data


class Command(BaseCommand):
    help = "Prepare session data for training an embedding model"

    def handle(self, *args, **options):
        sessions = prepare_session_data()

        # Ensure the TrainingData directory exists
        import os

        training_data_dir = os.path.join("nadooit_website", "TrainingData")
        if not os.path.exists(training_data_dir):
            os.makedirs(training_data_dir)

        # Save session data to a file
        output_file = os.path.join(training_data_dir, "session_data.txt")
        with open(output_file, "w") as outfile:
            for session in sessions:
                session_str = " ".join(str(signal) for signal in session)
                outfile.write(session_str + "\n")

        self.stdout.write(
            self.style.SUCCESS(f"Session data has been saved to {output_file}")
        )
