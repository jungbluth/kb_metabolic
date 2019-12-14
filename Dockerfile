FROM kbase/sdkbase2:python
MAINTAINER Sean Jungbluth <sjungbluth@lbl.gov>
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

WORKDIR /kb/module/bin

# To install all the dependencies
RUN apt-get update && apt-get install -y wget tzdata git r-base gcc automake libtool libc6-dev libxml2 libxml2-dev libxml-libxml-perl

RUN wget http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.16.tar.gz && tar -xvzf libiconv-1.16.tar.gz && cd libiconv-1.16 && ./configure --prefix=/usr/local/libiconv && make && make install

RUN cpan -r

RUN cpan -i Data::Dumper;
RUN cpan -i Excel::Writer::XLSX;
RUN cpan -i Getopt::Long;
RUN cpan -i Statistics::Descriptive;
RUN cpan -i Array::Split;
RUN cpan -i Bio::SeqIO;
RUN cpan -i Bio::Perl;
RUN cpan -i Bio::Tools::CodonTable;
RUN cpan -i Carp;

RUN wget http://eddylab.org/software/hmmer3/3.1b2/hmmer-3.1b2-linux-intel-x86_64.tar.gz && tar -xvzf hmmer-3.1b2-linux-intel-x86_64.tar.gz && cd hmmer-3.1b2-linux-intel-x86_64 && ./configure && make && make install && cd ../ && rm -rf hmmer-3.1b2-*

RUN wget https://github.com/hyattpd/Prodigal/releases/download/v2.6.3/prodigal.linux && mv prodigal.linux /usr/local/bin/prodigal && chmod +x /usr/local/bin/prodigal

RUN conda install -c bioconda sambamba

RUN conda install -c bioconda bamtools

RUN wget https://github.com/wwood/CoverM/releases/download/v0.3.1/coverm-x86_64-unknown-linux-musl-0.3.1.tar.gz && tar -xvf coverm-x86_64-unknown-linux-musl-0.3.1.tar.gz && mv coverm-x86_64-unknown-linux-musl-0.3.1/coverm /usr/local/bin/ && cd ../ && rm -rf coverm-*

RUN echo "install.packages(\"diagram\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"forcats\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"digest\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"htmltools\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"rmarkdown\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"reprex\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"tidyverse\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"stringi\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"ggthemes\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"ggalluvial\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"reshape2\", repos=\"https://cran.rstudio.com\")" | R --no-save
RUN echo "install.packages(\"ggraph\", repos=\"https://cran.rstudio.com\")" | R --no-save

# unclear why diamond is needed, but it is among the first steps run with the test data
RUN wget http://github.com/bbuchfink/diamond/releases/download/v0.9.27/diamond-linux64.tar.gz && tar xzf diamond-linux64.tar.gz && mv diamond /usr/local/bin/ && rm diamond-linux64.tar.gz

# need to fix so that the steps inside ./run_to_setup.sh are inside the entrypoint.sh file
RUN git clone https://github.com/AnantharamanLab/METABOLIC.git && cd METABOLIC && chmod +x ./run_to_setup.sh && ./run_to_setup.sh

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
