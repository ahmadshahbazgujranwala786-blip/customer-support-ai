from app.agents_registry import AGENT_REGISTRY
import traceback


print("AVAILABLE AGENTS:", AGENT_REGISTRY.keys())


class ExecutionManager:

    def __call__(self, state):

        print("🚀 EXECUTION MANAGER STARTED")

        tasks = state.get("tasks", [])

        print("TASKS RECEIVED:")
        print(tasks)


        results = []


        for task in tasks:

            try:

                agent_name = task.get("agent")

                print("\n==========================")
                print("REQUESTED AGENT:", agent_name)
                print("==========================")


                agent = AGENT_REGISTRY.get(agent_name)


                if not agent:
                    print(
                        f"❌ Agent {agent_name} not found"
                    )

                    results.append(
                        {
                            "agent": agent_name,
                            "status": "failed",
                            "error": "Agent not registered"
                        }
                    )

                    continue


                print(
                    f"▶ Running {agent_name}"
                )


                agent_state = {
                    **state,
                    "supervisor_instructions": task.get("instructions")
                }


                print(
                    "Calling function:",
                    agent.__name__
                )


                response = agent(
                    agent_state
                )


                print(
                    f"✅ {agent_name} finished"
                )

                print(
                    "Agent response:",
                    response
                )


                results.append(
                    {
                        "agent": agent_name,
                        "status": "completed",
                        "result": response
                    }
                )


            except Exception as e:

                print(
                    f"❌ Error in {agent_name}"
                )

                traceback.print_exc()


                results.append(
                    {
                        "agent": agent_name,
                        "status": "failed",
                        "error": str(e)
                    }
                )


        print(
            "✅ Execution Completed"
        )


        return {
            "agent_results": results
        }