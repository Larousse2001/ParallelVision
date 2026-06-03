# Rapport technique

## Multiprocessus
Le backend demarre un processus maitre qui cree plusieurs processus workers. Chaque worker execute un sous-ensemble des images. Le maitre distribue les taches et collecte les resultats. Cette separation permet de paralleliser les traitements et d utiliser plusieurs coeurs CPU.

## Multithreading
Chaque worker contient plusieurs threads. Les threads partagent la memoire du process et se repartissent les images recues. Cela permet d exploiter les latences internes des operations OpenCV et d amortir les couts de serialisation.

## IPC
- Pipes: le maitre envoie des commandes (START/STOP) aux workers.
- Shared Memory: les statistiques globales (total, traite, temps moyen, CPU) sont stockees dans une zone partagee.
- Message Queue: les workers envoient les resultats au maitre via une queue multiprocessing.

## Barbier endormi
Les images sont des clients. La file de taches est la salle d attente. Les workers (barbiers) attendent sur un semaphore. Lorsqu une image arrive, le semaphore est libere, ce qui reveille un worker. Le worker dort lorsqu il n y a plus d images.

## Philosophes dineurs
Avant de traiter une image, un worker doit obtenir deux ressources: un token CPU et un token GPU simule. Pour eviter le deadlock, l acquisition se fait avec un timeout et un backoff. Si le token GPU n est pas disponible, le token CPU est relache et le worker retente.

## Benchmarking
Le benchmark execute plusieurs configurations (1x1, 1x4, 2x4, 4x4, 8x8). Les mesures incluent le temps total, le temps moyen par image, l utilisation CPU, le speedup et l efficacite. Les resultats sont exportes en CSV dans `backend/benchmark/results.csv`.
