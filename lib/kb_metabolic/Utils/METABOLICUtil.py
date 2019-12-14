import os
import subprocess
import logging
import pandas as pd
import json


class MetabolicUtil():
    '''
    Utilities for running METABOLIC
    '''

    def __init__(self, config, callback_url, workspace_id, cpus):
        self.shared_folder = config['scratch']
        self.callback_url = callback_url
        self.cpus = cpus
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)


    def rename_input_file_suffixes(self):
        logging.info("Rename Genome File Suffixes\n")
        for filename in os.listdir(self.shared_folder):
            if filename.endswith(".fa", ".fna"):
                new_filename = "_".join(filename.split(".")[0:-1]) + ".fasta"
                os.rename(filename, new_filename)

    def run_metabolic_without_reads(self):
        '''
        Run the METABOLIC-G workflow (not using raw reads)
        '''
        out_dir = os.path.join(self.shared_folder, "output")
        metabolic_cmd = " ".join(["perl", "/kb/module/bin/METABOLIC/METABOLIC-G.pl",
                              "-in-gn", self.shared_folder,
                               "-t", str(self.cpus),
                               "-o", out_dir,
                               "-m", "/kb/module/bin/METABOLIC"])
        logging.info("Starting Command:\n" + metabolic_cmd)
        output = subprocess.check_output(metabolic_cmd, shell=True).decode('utf-8')
        logging.info(output)

        self._process_output_files(out_dir)
        return output

    def run_metabolic_with_reads(self):
        '''
        Run the METABOLIC-C workflow (using raw reads)
        '''
        out_dir = os.path.join(self.shared_folder, "output")
        omic_reads_parameter_file = 1 # need to fix when documentation better, currently unknown parameter
        metabolic_cmd = " ".join(["perl", "/kb/module/bin/METABOLIC/METABOLIC-C.pl",
                              "-in-gn", self.shared_folder,
                               "-t", str(self.cpus),
                               "-o", out_dir,
                               "-m", "/kb/module/bin/METABOLIC",
                               "-r", omic_reads_parameter_file])
        logging.info("Starting Command:\n" + metabolic_cmd)
        output = subprocess.check_output(metabolic_cmd, shell=True).decode('utf-8')
        logging.info(output)

        self._process_output_files(out_dir)
        return output

    def _process_output_files(self, out_dir):

        for path in (os.path.join(out_dir, 'gtdbtk.ar122.summary.tsv'),
                     os.path.join(out_dir, 'gtdbtk.bac120.summary.tsv'),
                     os.path.join(out_dir, 'gtdbtk.bac120.markers_summary.tsv'),
                     os.path.join(out_dir, 'gtdbtk.ar122.markers_summary.tsv'),
                     os.path.join(out_dir, 'gtdbtk.filtered.tsv')):
            try:
                summary_df = pd.read_csv(path, sep='\t', encoding='utf-8')
                outfile = path + '.json'
                summary_json = '{"data": ' + summary_df.to_json(orient='records') + '}'
                with open(outfile, 'w') as out:
                    out.write(summary_json)
            except Exception as exc:
                logging.info(exc)

        return
