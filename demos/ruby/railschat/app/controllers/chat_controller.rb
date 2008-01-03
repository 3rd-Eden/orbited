def user_keys
  list = []
  for user in $users do
    list = list + [user[0] + ", " + user[1].to_s + ", /railschat",]
  end
  
  return list
  # python: return ['%s, %s, /cherrychat' % (u, s) for u,s in self.users]
end

class ChatController < ApplicationController
  
  def index
  end
  
  def join
    user = params[:user]
    session = params[:session] || 0
    id = params[:id]
    
    if not $users.member?([user, session])
      $users = $users + [[user, session]]
      $orbit.event(user_keys(), '*' + user + ' joined*')
    end
     render :text => "ok"
  end
  
  def msg
    session = params[:session] || 0
    id = params[:id] || nil

    # $orbit.event(user_keys(), '<b>' + params[:user] + '</b> ' + params[:msg])
    $orbit.event(user_keys(), '' + params[:user] + ': ' + params[:msg])
    render :text => "ok"
  end
end

    # test if we have a users array.  if not, make one
    # begin
    #   $users
    # rescue
    #   $users = []
    # end
