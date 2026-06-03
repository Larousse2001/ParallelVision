import multiprocessing


def create_result_queue(ctx: multiprocessing.context.BaseContext) -> multiprocessing.Queue:
    return ctx.Queue()
