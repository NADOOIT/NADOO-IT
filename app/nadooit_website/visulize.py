import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from graphviz import Digraph
from collections import defaultdict
from django.core.serializers import serialize
import plotly.express as px

from .models import Session, Section, Session_Signal


def analyze_and_visualize_session_data():
    group_filter = "control"
    sessions, session_signals = load_session_data()
    validate_data(sessions, session_signals)

    section_transitions = create_section_transition_graph(session_signals, group_filter)
    visualize_section_transitions(section_transitions, group_filter)
    plot_interactive_section_transitions(section_transitions, group_filter)


def load_session_data():
    sessions = pd.DataFrame.from_records(Session.objects.values())
    session_signals = pd.DataFrame.from_records(Session_Signal.objects.values())

    print("Sessions columns:", sessions.columns)
    print("Session_Signals columns:", session_signals.columns)

    return sessions, session_signals


def validate_data(sessions, session_signals):
    # Check if there are any sections in the sessions DataFrame that are not present in the session_signals DataFrame
    missing_sections = set(sessions["section_id"]).difference(
        session_signals["section_id"]
    )
    if missing_sections:
        print(
            f"Warning: Missing section data for the following sections: {', '.join(map(str, missing_sections))}"
        )


def create_section_transition_graph(session_signals, group_filter=None):
    section_transitions = defaultdict(int)

    for _, session in session_signals.iterrows():
        if group_filter and session["variant"] != group_filter:
            continue

        if session["signal_type"] in ["revealed", "end_of_session_sections"]:
            from_section_id = session["from_section_id"]
            to_section_id = session["to_section_id"]
            section_transitions[(from_section_id, to_section_id)] += 1

    return section_transitions


def visualize_section_transitions(section_transitions, group_filter=None):
    dot = Digraph(comment="Section Transitions")
    for (from_section, to_section), count in section_transitions.items():
        dot.node(str(from_section), str(from_section))
        dot.node(str(to_section), str(to_section))
        dot.edge(str(from_section), str(to_section), label=str(count))

    output_filename = (
        f"section_transitions_{group_filter}.gv"
        if group_filter
        else "section_transitions.gv"
    )
    dot.render(output_filename, view=True)


def plot_interactive_section_transitions(section_transitions, group_filter=None):
    edges_df = pd.DataFrame(
        [
            {"from_section": from_section, "to_section": to_section, "count": count}
            for (from_section, to_section), count in section_transitions.items()
        ]
    )

    fig = px.sunburst(
        edges_df,
        path=["from_section", "to_section"],
        values="count",
        color="count",
        title=f'Section Transitions {"("+group_filter+")" if group_filter else ""}',
    )

    plot_filename = (
        f"section_transitions_{group_filter}.html"
        if group_filter
        else "section_transitions.html"
    )
    fig.write_html(plot_filename)
    fig.show()


if __name__ == "__main__":
    analyze_and_visualize_session_data()
