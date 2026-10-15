declare module "react-plotly.js" {
  import type { Component } from "react";
  import type { Config, Layout, Data } from "plotly.js";

  export interface PlotParams {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    style?: React.CSSProperties;
    className?: string;
    useResizeHandler?: boolean;
    onClick?: (event: Readonly<import("plotly.js").PlotMouseEvent>) => void;
  }

  export default class Plot extends Component<PlotParams> {}
}

declare module "plotly.js-dist-min" {
  import * as Plotly from "plotly.js";
  export = Plotly;
}
