"""
This example considers the following query::

    Fetch zirconium complexes with one or more hepta^5 ligands
    Afterwards, restrict the selection to those complexes which also have a metal node charge close to +1.5e.

"""

import functools
import os

import matplotlib.pyplot as plt
import numpy as np

import tmqmrdfdata as tmrdf


def job_fetch_Zi_hepta5(tmqmrdf, tmcs, context = None):
    partial_result = []

    tmqmrdf.fetch(tmcs = tmcs, auto_fetch_tmc_components = True, progress = False)
    
    for symbol, tmc in tmqmrdf.items("TMCs"):
        if tmc.centre()[1].symbol == "Zr":
            hit_hepta5 = False
            for ligand in tmc.ligands().values():
                _, ligand_species = tmqmrdf["ligand", ligand.symbol].ligand(
                    data = tmqmrdf.tbox.lgLrp.n_haptic_bound
                )

                if ligand_species.n_haptic_bound.value >= 5:
                    hit_hepta5 = True
                    break
            
            if hit_hepta5:
                charge = tmc.tmc(
                        data = tmqmrdf.tbox.cmTp.metal_node_natural_charge
                    )[1].metal_node_natural_charge.value
                partial_result.append((symbol, charge))

    return partial_result

if __name__ == "__main__":
    __spec__ = None
    
    # 1. Download data and initialise interface
    # =========================================
    if not os.path.exists("./temp/hdt-tmQM-RDF-v1.0.1"):
        if not os.path.exists("./temp"):
            os.makedirs("./temp")

        tmrdf.download_tmQM_RDF_knowledge_graph(dir = "./temp", version = "1.0.1", hdt_format = True)

    ds = tmrdf.TmqmRDF("./temp/hdt-tmQM-RDF-v1.0.1/")
    
    # 2. Extract CSD codes (and HOMO-LUMO gap) of target TMCs
    # =======================================================
    hits = tmrdf.concurrent_map(
        "./temp/hdt-tmQM-RDF-v1.0.1/", 
        job_fetch_Zi_hepta5,
        target = "TMCs",
        n_workers = 2
    )
    aggregated = functools.reduce(lambda x, y : x + y, hits)
    
    # 3. Inspect results
    # ==================
    print("First 10 hits:")
    for line in aggregated[:10]:
        print(f"\tCSD code: {line[0]}; Metal charge: {line[1]:.4f} e")
    print()

    charge = np.array([line[1] for line in aggregated])
    mu, sd = np.mean(charge), np.std(charge)
    print(f"Mean metal charge for hepta 5 / Zr complexes: {mu:.4f} +- {sd:.4f} e")

    # 3.1 select complexes with charge close to +1.5e
    # -----------------------------------------------
    selected_hits = [
        line for line in aggregated
        if line[1] >= 1.5 - sd and line[1] <= 1.5 + sd
    ]

    print()
    print("First 10 hits with charge ~ +1.5e:")
    for line in selected_hits[:10]:
        print(f"\tCSD code: {line[0]}; Metal charge: {line[1]:.4f} e")

    # 3.2 Plot metal charge histogram
    # -------------------------------
    fig, ax = plt.subplots()
    ax.hist(charge, bins = 50)

    ax.set_xlabel("Metal node charge")
    ax.set_ylabel("Counts")

    ax.axvline(x = mu, ls = "dashed", c = "black")
    ax.text(mu*0.8, 0.97, "Mean", color = "black", transform = ax.get_xaxis_transform())

    ax.axvline(x = 1.5, ls = "solid", c = "red")
    ax.text(1.5*0.8, 0.97, "Target", color = "red", transform = ax.get_xaxis_transform())
    ax.fill_betweenx([0, 1], 1.5 - sd, 1.5 + sd, color = (1., 0, 0, 0.2), transform = ax.get_xaxis_transform())

    fig.savefig("./query_Zn_hepta5_metalcharge1.5.png", format = "png", bbox_inches = "tight")
