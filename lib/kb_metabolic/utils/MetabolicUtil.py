import os
import subprocess
import logging


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

    def stage_reads_list_file(self, reads_list):
        """
        stage_reads_list_file: download fastq file associated to reads to scratch area
                          and return result_file_path
        """

        log('Processing reads object list: {}'.format(reads_list))

        result_file_path = []
        read_type = []

        # getting from workspace and writing to scratch. The 'reads' dictionary now has file paths to scratch.
        reads = self.ru.download_reads({'read_libraries': reads_list, 'interleaved': None})['files']

        # reads_list is the list of file paths on workspace? (i.e. 12804/1/1).
        # "reads" is the hash of hashes where key is "12804/1/1" or in this case, read_obj and
        # "files" is the secondary key. The tertiary keys are "fwd" and "rev", as well as others.
        for read_obj in reads_list:
            files = reads[read_obj]['files']    # 'files' is dictionary where 'fwd' is key of file path on scratch.
            result_file_path.append(files['fwd'])
            read_type.append(files['type'])
            if 'rev' in files and files['rev'] is not None:
                result_file_path.append(files['rev'])

        return result_file_path, read_type


    def deinterlace_raw_reads(self, fastq):
        fastq_forward = fastq.split('.fastq')[0] + "_forward.fastq"
        fastq_reverse = fastq.split('.fastq')[0] + "_reverse.fastq"
        command = 'reformat.sh in={} out1={} out2={} overwrite=true'.format(fastq, fastq_forward, fastq_reverse)
        self._run_command(command)
        return (fastq_forward, fastq_reverse)


    def prepare_input_read_files(self, params):

        reads_list = task_params['reads_list']

        (read_scratch_path, read_type) = self.stage_reads_list_file(reads_list)

        # list of reads files, can be 1 or more. assuming reads are either type unpaired or interleaved
        # will not handle unpaired forward and reverse reads input as seperate (non-interleaved) files

        for i in range(len(read_scratch_path)):
            fastq = read_scratch_path[i]
            fastq_type = read_type[i]

            if fastq_type == 'interleaved':  # make sure working - needs tests
                log("Running interleaved read mapping mode")
                self.run_read_mapping_interleaved_pairs_mode(task_params, assembly_clean, fastq, sam)
            else:  # running read mapping in single-end mode
                log("Running unpaired read mapping mode")
                self.run_read_mapping_unpaired_mode(task_params, assembly_clean, fastq, sam)



    def run_metabolic_without_reads(self, params):
        '''
        Run the METABOLIC-G workflow (not using raw reads)
        '''
        out_dir = os.path.join(self.shared_folder, "output")
        metabolic_cmd = " ".join(["perl", "/kb/module/bin/METABOLIC/METABOLIC-G.pl",
                                  "-in-gn", self.shared_folder,
                                  "-t", str(self.cpus),
                                  "-m-cutoff", params['kegg_module_cutoff'],
                                  "-p", params['prodigal_method'],
                                  "-o", out_dir,
                                  "-m", "/data/METABOLIC"])
        logging.info("Starting Command:\n" + metabolic_cmd)
        output = subprocess.check_output(metabolic_cmd, shell=True).decode('utf-8')
        logging.info(output)

        # self._process_output_files(out_dir)
        return output

    def run_metabolic_with_reads(self, params):
        '''
        Run the METABOLIC-C workflow (using raw reads)
        '''
        out_dir = os.path.join(self.shared_folder, "output")
        omic_reads_parameter_file = 1  # need to fix when documentation better, currently unknown parameter
        metabolic_cmd = " ".join(["perl", "/kb/module/bin/METABOLIC/METABOLIC-C.pl",
                                  "-in-gn", self.shared_folder,
                                  "-t", str(self.cpus),
                                  "-m-cutoff", params['kegg_module_cutoff'],
                                  "-p", params['prodigal_method'],
                                  "-o", out_dir,
                                  "-m", "/data/METABOLIC",
                                  "-r", omic_reads_parameter_file])
        logging.info("Starting Command:\n" + metabolic_cmd)
        output = subprocess.check_output(metabolic_cmd, shell=True).decode('utf-8')
        logging.info(output)

        # self._process_output_files(out_dir)
        return output
    #
    # def _process_output_files(self, out_dir):
    #
    #     for path in (os.path.join(out_dir, 'gtdbtk.ar122.summary.tsv'),
    #                  os.path.join(out_dir, 'gtdbtk.bac120.summary.tsv'),
    #                  os.path.join(out_dir, 'gtdbtk.bac120.markers_summary.tsv'),
    #                  os.path.join(out_dir, 'gtdbtk.ar122.markers_summary.tsv'),
    #                  os.path.join(out_dir, 'gtdbtk.filtered.tsv')):
    #         try:
    #             summary_df = pd.read_csv(path, sep='\t', encoding='utf-8')
    #             outfile = path + '.json'
    #             summary_json = '{"data": ' + summary_df.to_json(orient='records') + '}'
    #             with open(outfile, 'w') as out:
    #                 out.write(summary_json)
    #         except Exception as exc:
    #             logging.info(exc)
    #
    #     return
