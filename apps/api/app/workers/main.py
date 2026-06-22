"""Background worker: drains the Redis queue and runs the compiler + evaluator."""


def main() -> None:
    # TODO: subscribe to the queue; on a new session, compile the graph; on a new
    # agent run, evaluate it and persist metrics + failure summary.
    print("agentreplay worker started")


if __name__ == "__main__":
    main()
