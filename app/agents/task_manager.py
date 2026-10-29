def get_tasks(state, agent_name):

    tasks = state.get(
        "tasks",
        []
    )

    return [
        task
        for task in tasks
        if task.get("agent") == agent_name 
    ]