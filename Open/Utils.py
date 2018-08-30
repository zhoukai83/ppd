

def terminate_signal_triggered(logger):
    with open("terminate.txt") as f:
        terminate_signal = f.read()
        if terminate_signal == "True":
            logger.info("terminate")
            return True

    return False

def trigger_terminate_signal():
    with open("terminate.txt", "w") as f:
        f.write("True")

def restore_terminate_signal():
    with open("terminate.txt", "w") as f:
        f.write("Tru")