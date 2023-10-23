type Cell = {
  cell_type: string;
  execution_count: number | null;
  id: string;
  metadata: object;
  outputs: object[];
  source: string[];
};

type MetaData = {
  kernelspec: {
    display_name: string;
    language: string;
    name: string;
  };
  language_info: {
    file_extension: string;
    mimetype: string;
    name: string;
  };
};

export type Content = {
  cells: Cell[];
  metadata: MetaData;
  nbformat: number;
  nbformat_minor: number;
};
