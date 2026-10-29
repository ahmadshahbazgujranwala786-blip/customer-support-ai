class ResponseAggregator:

    print("ResponseAggregator class defined successfully.")
    def __call__(self,state):

        results = state.get(
            "agent_results",
            []
        )


        response_parts = []


        for item in results:

            response_parts.append(
                str(
                    item.get("result")
                )
            )


        final_response = "\n\n".join(
            response_parts
        )


        return {

            "final_response":
                final_response

        }