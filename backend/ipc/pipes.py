from typing import List, Tuple
import multiprocessing


def create_pipes(count: int) -> List[Tuple[multiprocessing.connection.Connection, multiprocessing.connection.Connection]]:
    pipes = []
    for _ in range(count):
        parent_conn, child_conn = multiprocessing.Pipe(duplex=True)
        pipes.append((parent_conn, child_conn))
    return pipes
