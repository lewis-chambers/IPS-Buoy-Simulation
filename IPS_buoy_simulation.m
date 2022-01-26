%% Input Variables
% Wave Data
T = 7.8;
F = 1/T;
omega = 2*pi*F;
Hs = 2.4;

% Sim Data
t_range = [0 T*20];
xt = linspace(t_range(1),t_range(2),1000)';
x = Hs * sin(2*pi*F*xt);
x_p = [0; diff(x)];

% Constants
rho = 1025;
g = 9.81;

% Device Data
added_mass_ratio = 0.5;
r_buoy = 7.5;
L_buoy = 10; %cylinder shape only
shape_buoy = "sphere";

tube_L_max = 14;
tube_r_max = 7;

m1 = 9.057e5* (1+added_mass_ratio);
m2 = m1*1;

m2_max_ratio = (rho * pi * tube_r_max^2 * tube_L_max)/m1;

tube_radius = sqrt(m2 / (rho * pi * tube_L_max));
tube_length = tube_L_max;
s = pi * r_buoy^2;

% Stats
K_resonance = (m1*m2*omega^2)/(m1+m2);
% PTO Data
C_wave = 3e5;
C_damper = 3e6;
K = 0;

% Equilibrium depth (dependent on shape)
switch shape_buoy
    case "sphere"
        y_buoy_bottom = sphere_equilibrium(r_buoy,m1,rho);
    case "cylinder"
        y_buoy_bottom = cylinder_equilibrium(r_buoy,m1,rho);
end
%% Simulation

% Simulation Initialization
fprintf("Initializing simulation array...")
metadata = struct('t_range', t_range, 'xt', xt, 'x', x, 'x_p', x);

base_variables = struct('T', T, 'F', F, 'omega', omega, 'Hs', Hs, 'rho', rho, 'g',g,...
    'r_buoy', r_buoy, 'm1', m1, 'm2', m2, 'C_wave', C_wave, 'C_damper', C_damper, 'K', K,...
    'L_max', tube_L_max, 'r_max', tube_r_max,...
    'L_buoy', L_buoy, 'shape_buoy', char(shape_buoy),...
    'tube_length', tube_length, 'tube_radius', tube_radius,...
    'buoy_equilibrium', y_buoy_bottom);
   
fprintf("Done!\n")

% Simulation running
sim_out = run_simulation(base_variables, metadata, t_range);

% Post Processing
fprintf("Processing Data...")
sim_processed = process_data(sim_out, x, xt);
fprintf("Done!\n")
%% Plotting
%plot_single_sim(sim_processed);
%% Animation Section
speed = 3;
scale = 5;
filename = "demo_file.mat";
executable = 'dir_exe'; % ['python', 'single_exe', 'dir_exe']

data = get_animation_data(sim_processed);
animate_IPS_buoy(data, base_variables, speed, scale, filename, executable);
%% Functions
function dydt = model(t,y, ode_vars)
    xt = ode_vars.xt;
    x = ode_vars.x;
    x_p = ode_vars.x_p;
    g = ode_vars.g;
    rho = ode_vars.rho;
    r_buoy = ode_vars.r_buoy;
    L_buoy = ode_vars.L_buoy;
    shape_buoy = ode_vars.shape_buoy;
    m1 = ode_vars.m1;
    m2 = ode_vars.m2;
    C_wave = ode_vars.C_wave;
    C_damper = ode_vars.C_damper;
    K = ode_vars.K;

    x = interp1(xt,x,t);
    x_p = interp1(xt,x_p,t);
    
    y1 = y(1); y1_p = y(2); y2 = y(3); y2_p = y(4);
    
    y1_submersion = y1-x;
    
    %% Assigning Outputs [y1, y1', y2, y2']
    dydt = zeros(size(y));
    
    dydt(1) = y1_p;
    
    if y1_submersion < 0 %If buoy exits water, there's no buoyancy force
        dydt(2) = ((m1*g) - (0) + (C_damper*(y2_p-y1_p)) + (K*(y2-y1)) - (C_wave*(y1_p-x_p)) )/m1;
    else %if buoy in water, Fb is rho*g*V, V depending on depth and shape of buoy
        switch shape_buoy
            case "sphere"
                volume = sphere_volume(r_buoy,y1_submersion);
            case "cylinder"
                volume = cylinder_volume(r_buoy,y1_submersion, L_buoy);
        end
        dydt(2) = ((m1*g) - (rho*g*volume) + (C_damper*(y2_p-y1_p)) + (K*(y2-y1)) - (C_wave*(y1_p-x_p)) )/m1;
    end
    
    dydt(3) = y2_p;
    
    dydt(4) = (-(K*(y2-y1)) - (C_damper*(y2_p-y1_p)))/m2;
    
    function volume = sphere_volume(r, h)
        if h >= r*2
            volume = (4/3)*pi*r^3;
        else
            r_bottom = sqrt(h*((2*r)-h));
            volume = (pi/6)*h*((3*r_bottom^2)+(h^2));
        end
    end
    function volume = cylinder_volume(r,h,L_buoy)
        if h >= L_buoy
            volume = L_buoy * pi * r^2;
        else
            volume = h * pi * r^2;
        end
    end
end

function plot_single_sim(data_in, title_str)
    
    data = data_in.data;
    
    if ~exist('title_str', 'var')
        title_str = '';
    else
        if ~isstring(title_str)
            title_str = string(title_str);
        end
    end
    
    y1_d = data.motion.displacement.buoy.data;
    y1_v = data.motion.velocity.buoy.data;
    y2_d = data.motion.displacement.piston.data;
    y2_v = data.motion.velocity.piston.data;
    
    d_relative = data.motion.displacement.relative.data;
    v_relative = data.motion.velocity.relative.data;
    
    %%%%%%%%%%%%%%%% ABSOLUTE MOTION %%%%%%%%%%%%%%%%%%%%%%%%
    figure
    subplot(2,1,1)
    plot(data.time,[y1_d, y2_d])

    legend(["Buoy", "Piston"])
    title(sprintf("Displacement of Bodies%s", title_str))
    ylabel("Displacement (m)")
    
    subplot(2,1,2)
    plot(data.time,[y1_v, y2_v])

    legend(["Buoy", "Piston"])
    title(sprintf("Velocity of Bodies%s", title_str))
    ylabel("Velocity (m/s)")
    linkaxes(findall(gcf,'Type','Axes'), 'x')
    xlabel("Time (s)")
    
    %%%%%%%%%%%%%%%%%%%%%%%%% RELATIVE MOTION %%%%%%%%%%%%%%%%%%%%%%%%%%%%
    stats = ["mean_peak"];
    figure
    
    subplot(2,1,1)
    plot(data.time, d_relative)
    hold on
    zero_arr = zeros(size(d_relative));
    plot(data.time, [zero_arr + (data_in.L_max/2), zero_arr - (data_in.L_max/2)], '-r')
    plot(data.time, [zero_arr + (data_in.L_max*0.005), zero_arr - (data_in.L_max*0.005)], '-g')
    
    plot_stats("mean_peak", data.motion.displacement, "relative", data.time([1 end],1))
    legend(["Data", "Tube Ends","","Min Motion","", replace(stats,'_', ' ')], 'Location', 'best')
    
    ylabel("Displacement (m)")
    title(sprintf("Relative Displacement%s", title_str))
    
    subplot(2,1,2)
    plot(data.time, v_relative)
    xlabel("Time (s)")
    ylabel("Velocity (m/s)")
    title(sprintf("Relative Velocity%s", title_str))
    linkaxes(findall(gcf,'Type','Axes'), 'x')
    
    %%%%%%%%%%%%%%%%%%%% FORCES %%%%%%%%%%%%%%%%%%%%%%%%
    stats = ["mean", "trimmed_mean"];
    
    figure
    subplot(3,1,1)
    plot(data.time, data.force.damper.data/1000)
    ylabel("Force (kN)")
    title(sprintf("Damper%s", title_str))
    plot_stats(stats, data.force, "damper", data.time([1 end],1),1e-3)
    legend(["Data", replace(stats,'_', ' ')], 'Location', 'best')
    
    subplot(3,1,2)
    plot(data.time, data.force.spring.data/1000)
    ylabel("Force (kN)")
    title(sprintf("Spring%s", title_str))
    plot_stats(stats, data.force, "spring", data.time([1 end],1),1e-3)
    
    
    subplot(3,1,3)
    plot(data.time, data.force.total.data/1000)
    ylabel("Force (kN)")
    title(sprintf("Total%s", title_str))
    plot_stats(stats, data.force, "total", data.time([1 end],1),1e-3)
    
    linkaxes(findall(gcf,'Type','Axes'), 'x')
    xlabel("Time (s)")
    
    %%%%%%%%%%%%%%%%% POWERS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    figure
    subplot(3,1,1)
    plot(data.time, data.power.damper.data/1000)
    plot_stats(stats, data.power, "damper", data.time([1 end],1),1e-3)
    ylabel("Power (kW)")
    title(sprintf("Damper%s", title_str))
    legend(["Data", replace(stats,'_', ' ')], 'Location', 'best')
    
    subplot(3,1,2)
    hold on
    plot(data.time, data.power.spring.data/1000)
    plot_stats(stats, data.power, "spring", data.time([1 end],1),1e-3)
    
    ylabel("Power (kW)")
    title(sprintf("Spring%s", title_str))
    
    subplot(3,1,3)
    plot(data.time, data.power.total.data/1000)
    plot_stats(stats, data.power, "total", data.time([1 end],1),1e-3)
    ylabel("Power (kW)")
    title(sprintf("Total%s", title_str))
    
    linkaxes(findall(gcf,'Type','Axes'), 'x')
    xlabel("Time (s)")
    
    function plot_stats(stat_list, data, source, time_arr, scale_factor)
        if ~exist('scale_factor','var')
            scale_factor = 1;
        end
        
        opts = ["min", "mean", "max", "rms",...
        "trimmed_min", "trimmed_mean", "trimmed_max", "trimmed_rms",...
        "mean_peak"];
        
        if ~isstring(stat_list)
            stat_list = string(stat_list);
        end
        
        if any(~ismember(stat_list, opts))
            error('"%s" not valid, pick from:\n\n%s',...
                strjoin(stat_list(~ismember(stat_list, opts)),'", "'),...
                sprintf("%s\n", opts));
        else
            
            matrix = nan(2, numel(stat_list));

            for i = 1 : numel(stat_list)
                matrix(:,i) = repmat(data.(source).(stat_list(i))*scale_factor,2,1);
            end
            hold on
            plot(time_arr, matrix, '-.')
        end
    end
end
  
function plot_power(data_in, simulation_vars, opt, source, trim_opts)
    valid_params = ["min", "mean", "max", "rms",...
        "trimmed_min", "trimmed_mean", "trimmed_max", "trimmed_rms",...
        "mean_peak"];
    
    valid_source = ["damper", "spring", "total"];
    valid_trim = ["exit_tube", "invalid_tube", "silly_motion", "exit_water"];
    
    if ~exist('opt', 'var') || ~ismember(opt, valid_params)
        error(sprintf("You must use one of the following:\n\n") + sprintf("%s\n", valid_params));
    end
    
    if ~exist('source', 'var') || ~ismember(source, valid_source)
        error(sprintf("You must use one of the following:\n\n") + sprintf("%s\n", valid_source));
    end
    
    if exist('trim_opts', 'var')
        trim_opts = string(trim_opts);
        if any(~ismember(trim_opts, valid_trim))
            error(sprintf("You must use one of the following:\n\n") + sprintf("%s\n", valid_trim));
        end
    end
    
    if ~isstring(opt)
        opt = string(opt);
    end
    
    power = cellfun(@(c)c.data.power.(source).(opt), data_in);
    
    if exist('trim_opts', 'var')
        idx = false(size(power));
        
        for i = 1 : numel(trim_opts)
            switch trim_opts(i)
                case "exit_tube"
                    rel = cellfun(@(c) abs(c.data.motion.displacement.relative.mean_peak), data_in);
                    max_rel = cellfun(@(c) abs(c.data.motion.displacement.relative.max), data_in);
                    min_rel = cellfun(@(c) abs(c.data.motion.displacement.relative.min), data_in);
                    max_rel(min_rel > max_rel) = min_rel(min_rel > max_rel);
                    rel(isnan(rel)) = max_rel(isnan(rel));
                    idx(max_rel > data_in{1,1}.L_max/2) = true;
                case "invalid_tube"
                    tube_radius = cellfun(@(c)c.tube_radius, data_in);
                    r_max = cellfun(@(c)c.r_max, data_in); 
                    idx(tube_radius > r_max) = true;
                case "silly_motion"
                    rel = cellfun(@(c) c.data.motion.displacement.relative.mean_peak, data_in);
                    idx(rel < data_in{1,1}.L_max * 0.005) = true;
                case "exit_water"
                    rel = cellfun(@(c) c.data.motion.displacement.buoy.mean_min_peak, data_in);
                    idx(rel < 0) = true;
            end
        end
        power(idx) = nan;
    end
    
    figure
    hold on
    grid
    opt = char(opt);
    power_label = sprintf("%s Power (kW)", string([upper(opt(1)), lower(opt(2:end))]));
    
    if any(size(power) == 1)
        X = simulation_vars{1,1}{2};
        plot(X, power/1000,'ButtonDownFcn', @plot_point);
        
        xlabel(replace(simulation_vars{1,1}{1},'_',' '))
        ylabel(replace(power_label, '_', ' '))
        title(string([upper(source(1)), lower(source(2:end))]))
        
        if mean(X) / max(X) < 0.45
            set(gca, 'XScale', 'log')
        end
        
        xlim([min(X), max(X)])
    else
        X = reshape(simulation_vars{1,1}{2}, size(power));
        Y = reshape(simulation_vars{1,2}{2}, size(power));
        mesh(X, Y, power/1000,'ButtonDownFcn', @plot_point)
        
        xlabel(replace(simulation_vars{1,1}{1}, '_', ' '))
        ylabel(replace(simulation_vars{1,2}{1}, '_', ' '))
        zlabel(replace(power_label, '_', ' '))
        title(string([upper(source(1)), lower(source(2:end))]))
        
        ax = gca;
        
        set(ax,'View', [-30 30]);
        
        if mean(unique(abs(X))) / max(unique(abs(X))) < 0.45
            set(ax, 'XScale', 'log')
        end
        
        if mean(unique(abs(Y))) / max(unique(abs(Y))) < 0.45
            set(ax, 'YScale', 'log')
        end
        xlim([min(unique(X)), max(unique(X))])
        ylim([min(unique(Y)), max(unique(Y))])
%         set(gca, 'ZScale', 'log')
    end
    
end

function simulation = process_data(simulation,x,xt)  

    sim_data = simulation.data;

    x_adj = interp1(xt,x,simulation.data.time);

    y1_d = sim_data.motion(:,1);
    y1_v = sim_data.motion(:,2);
    y2_d = sim_data.motion(:,3);
    y2_v = sim_data.motion(:,4);

    d_relative = y2_d - y1_d;
    v_relative = y2_v - y1_v;

    force_damper = simulation.C_damper * v_relative;
    force_spring = simulation.K * d_relative;
    force_total = force_damper + force_spring;

    power_damper = force_damper .* v_relative;
    power_spring = force_spring .* v_relative;
    power_total = power_damper + power_spring;

    displacement_struct = struct(...
        'buoy',add_stats(y1_d),...
        'piston', add_stats(y2_d),...
        'relative', add_stats(d_relative)...
        );
    velocity_struct = struct(...
        'buoy',add_stats(y1_v),...
        'piston', add_stats(y2_v),...
        'relative', add_stats(v_relative)...
        );

    force_struct = struct(...
        'damper', add_stats(force_damper),...
        'spring', add_stats(force_spring),...
        'total', add_stats(force_total)...
        );

    power_struct = struct(...
        'damper', add_stats(power_damper),...
        'spring', add_stats(power_spring),...
        'total', add_stats(power_total)...
        );

    simulation.data.force = force_struct;
    simulation.data.power = power_struct;

    simulation.data = rmfield(simulation.data,'motion');

    simulation.data.motion.displacement = displacement_struct;
    simulation.data.motion.velocity = velocity_struct;

    simulation.data.wave_profile = x_adj;
end

function out = add_stats(data)
        %looks for end of transient
        try
            change_pnt = findchangepts(data);
            change_pnt = change_pnt(end);
        catch
            change_pnt = 1;
        end
        % if transient occurs more than a third in, it is ignored and uses
        % the regular mean
        if change_pnt > numel(data)*0.3
            change_pnt = 1;
        end
        
        out = struct(...
            'data', data,...
            'min', min(rmoutliers(data)),...
            'max', max(rmoutliers(data)),...
            'mean', mean(rmoutliers(data)),...
            'rms', rms(rmoutliers(data)),...
            'trimmed_min', min(data(change_pnt:end)),...
            'trimmed_mean', mean(data(change_pnt:end)),...
            'trimmed_max', max(data(change_pnt:end)),...
            'trimmed_rms', rms(data(change_pnt:end))...
            );
        try
            [pk_max, ~] = findpeaks(rmoutliers(data));
            [pk_min, ~] = findpeaks(rmoutliers(-data));
            
            pk_max(pk_max <= 0) = [];
            pk_min(pk_min <= 0) = [];
            
            out.mean_peak = mean(pk_max);
            out.mean_min_peak = -mean(pk_min);
        catch
            out.mean_pk = [];
        end
    end

function out = get_average_peak(data)
    try
        [pk, ~] = findpeaks(data);
        pk = pk(pk > 0);
        out = mean(pk);
    catch
        out = 0;
    end
end

function simulation = run_simulation(simulation, metadata, t_range)
    xt = metadata.xt;
    x = metadata.x;
    x_p = metadata.x_p;

    ode_vars = struct('xt', xt, 'x', x, 'x_p', x_p, 'g', simulation.g,...
        'rho', simulation.rho, 'r_buoy', simulation.r_buoy, 'm1', simulation.m1,...
        'm2', simulation.m2, 'C_wave', simulation.C_wave, 'C_damper',...
        simulation.C_damper, 'K', simulation.K, 'L_buoy', simulation.L_buoy,...
        'shape_buoy', simulation.shape_buoy);

    IC = [simulation.buoy_equilibrium; 0; simulation.buoy_equilibrium; 0]; % [y1, y1', y2, y2'] sim starts at equilibrium

    [t,y] = ode45(@(t,y) model(t,y,ode_vars), t_range, IC);

    simulation.data = struct('motion', y, 'time', t);
    
end

function plot_point(src, eventdata)
        assignin('base', 'eventdata', eventdata)
        x = eventdata.IntersectionPoint(1);
        y = eventdata.IntersectionPoint(2);
        z = eventdata.IntersectionPoint(3);
        
        x_vals = src.XData(1,:);
        y_vals = src.YData(:,1);
        z_vals = src.ZData;

        [~,ix] = min(abs(abs(x_vals) - abs(x)));
        [~,iy] = min(abs(abs(y_vals) - abs(y)));
        

        val_x = x_vals(ix);
        val_y = y_vals(iy);
        val_z = z_vals(iy,ix);

        ax = gca;

        
        if numel(eventdata.Source.Children) > 0
            delete(eventdata.Source.Children);
        end
        
        index = (numel(y_vals) * (ix-1)) + iy;
        datatip(ax.Children, 'DataIndex',index);
        
        data = evalin('base','sim_processed');
        
        if ~isempty(z_vals)
            title_str = sprintf("\nX:%.5g [%i], Y:%.5g [%i], Z:%.5g, ID:%i", val_x, ix, val_y, iy,val_z, data{iy,ix}.ID);
            plot_single_sim(data, [ix,iy], false, title_str)
        else
            title_str = sprintf("\nX:%.5g [%i], Y:%.5g [%i], ID:%i", ix,val_x, iy,val_y, data{iy,ix}.ID);
            plot_single_sim(data, ix,false, title_str)
        end
end

function out = sphere_equilibrium(r,m,rho)
    out = fmincon(@(h) abs(((pi.*h.^2)./(3)).*((3.*r)-h) - m/rho),r,...
        [],[],[],[],0,r*2,[],optimoptions('fmincon','Display', 'off'));
end

function out = cylinder_equilibrium(r,m,rho)
    out = (m)/(rho*pi*r^2);
end

function sim_data = get_animation_data(simulation)
    sim_data = struct(...
        'buoy_equilibrium', simulation.buoy_equilibrium,...
        'buoy_motion', (simulation.data.motion.displacement.buoy.data - simulation.buoy_equilibrium)',...
        'piston_motion', (simulation.data.motion.displacement.piston.data - simulation.buoy_equilibrium)',...
        'wave_motion', simulation.data.wave_profile',...
        'time', simulation.data.time',...
        'buoy_shape', simulation.shape_buoy,...
        'buoy_radius', simulation.r_buoy,...
        'buoy_length', simulation.L_buoy,...
        'tube_length', simulation.tube_length,...
        'tube_radius', simulation.tube_radius...
    );
end

function animate_IPS_buoy(simulation, simulation_data, speed, scale, filename, executable)

if ~exist('speed', 'var')
    speed = 5;
end

if ~exist('scale', 'var')
    scale = 1;
end

simulation.buoy_shape = char(simulation.buoy_shape);
script_name = 'make_animation';

save(filename, 'simulation', 'simulation_data', 'speed', 'scale', '-v7')

disp('Opening Animation')

switch lower(executable)
    case 'python'
        script_name = strcat(script_name, ".py");
        command = strcat('python', " ", script_name, " ", filename, " &");
    case 'dir_exe'
        script_name = strcat("make_animation\", script_name, ".exe");
        command = strcat(script_name, " ", filename, " &");
    case 'single_exe'
        script_name = strcat(script_name, ".exe");
        command = strcat(script_name, " ", filename, " &");
    otherwise
        error("executable must be one of: 'python','single_exe', 'dir_exe'")
end

system(command);
disp('Give it a sec')

end
