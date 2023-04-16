import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from graphviz import Digraph
from collections import defaultdict
from django.core.serializers import serialize
import click
import plotly.express as px

from .models import Session, Section, Session_Signals


@click.command()
@click.option(
    "--group-filter", default=None, help="Filter by control or experimental group"
)
def analyze_and_visualize_session_data(group_filter):
    sessions, session_signals = load_session_data()
    validate_data(sessions, session_signals)

    section_transitions = create_section_transition_graph(session_signals, group_filter)
    visualize_section_transitions(section_transitions, group_filter)
    plot_interactive_section_transitions(section_transitions, group_filter)


def load_session_data():
    sessions = serialize("json", Session.objects.all())
    session_signals = serialize("json", Session_Signals.objects.all())
    return pd.read_json(sessions), pd.read_json(session_signals)


def validate_data(sessions, session_signals):
    missing_sessions = set(session_signals["session_id"]).difference(
        set(sessions["session_id"])
    )

    if missing_sessions:
        raise ValueError(
            f"Session signals reference missing sessions: {missing_sessions}"
        )

    missing_sections = set(session_signals["section_id"]).difference(
        set(Section.objects.values_list("section_id", flat=True))
    )

    if missing_sections:
        raise ValueError(
            f"Session signals reference missing sections: {missing_sections}"
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
