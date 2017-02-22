R=$1
$R --vanilla<<EOL
source("https://bioconductor.org/biocLite.R")
biocLite()
install.packages("devtools", repos='http://cran.us.r-project.org')
devtools::install_github("pbreheny/deepn")
EOL
